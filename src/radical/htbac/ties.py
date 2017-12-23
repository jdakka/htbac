import numpy as np
import parmed as pmd
import uuid

import radical.utils as ru
from radical.entk import Pipeline, Stage, Task


NAMD2 = '/u/sciteam/jphillip/NAMD_LATEST_CRAY-XE-MPI-BlueWaters/namd2'
NAMD_TI_ANALYSIS = "/u/sciteam/farkaspa/namd/ti/namd2_ti.pl"
_simulation_file_suffixes = ['.coor', '.xsc', '.vel']
_reduced_steps = dict(min=100, eq1=3000, eq2=1000, prod=2000)
_full_steps = dict(min=1000, eq1=30000, eq2=970000, prod=2000000)


class Ties(object):

    def __init__(self, number_of_replicas, number_of_windows=0, additional=None,
                 systems=list(), workflow=None, cores=64, ligand=False, full=False):

        self.number_of_replicas = number_of_replicas
        self.lambdas = np.linspace(0.0, 1.0, number_of_windows, endpoint=True)
        self.lambdas = np.append(self.lambdas, additional)
        self.ligand = '-ligands' if ligand else ''
        self.step_count = _full_steps if full else _reduced_steps
        self.instances = 0 
        
        self.systems = systems
        print self.systems
        self.instances = len(self.systems)
        self.cores = cores
        self._id = uuid.uuid1()  # generate id

        self.workflow = workflow or ['min', 'eq1', 'eq2', 'prod']
        
        # Profiler for TIES PoE

        self._uid = ru.generate_id('radical.htbac.ties')
        self._logger = ru.get_logger('radical.htbac.ties')
        self._prof = ru.Profiler(name=self._uid)
        self._prof.prof('create ties instance', uid=self._uid)

    def id(self):
        return self._id

    # Generate a new pipeline
    def generate_pipeline(self, previous_pipeline=None):

        pipeline = Pipeline()

        # Simulation stages
        # =================

        for step in self.workflow:
            stage = Stage()
            stage.name = step
            print stage.name

            for system in self.systems:
                self.box = pmd.amber.AmberAsciiRestart('systems/ties{lig}/{s}/build/{s}-complex.crd'.format(lig=self.ligand, s=system)).box            
                    
                for replica in range(self.number_of_replicas):
                    for ld in self.lambdas:

                    
                        task = Task()
                        task.name = 'system_{}_replica_{}_lambda_{}'.format(system, replica, ld)


                        task.arguments += ['ties-{}.conf'.format(stage.name)]
                        task.copy_input_data = ['$SHARED/ties-{}.conf'.format(stage.name)]
                        task.executable = [NAMD2]

                        task.mpi = True
                        task.cores = self.cores

                        links = []
                        links += ['$SHARED/{}-complex.top'.format(system), '$SHARED/{}-tags.pdb'.format(system)]
                        print links
                        if self.workflow.index(step):
                            previous_stage = pipeline.stages[-1]
                            previous_task = next(t for t in previous_stage.tasks if t.name == task.name)
                            path = '$Pipeline_{}_Stage_{}_Task_{}/'.format(pipeline.uid, previous_stage.uid, previous_task.uid)
                            links += [path+previous_stage.name+suffix for suffix in _simulation_file_suffixes]
                        else:
                            links += ['$SHARED/{}-complex.pdb'.format(system)]

                        task.link_input_data = links

                        task.pre_exec += ["sed -i 's/BOX_X/{}/g' *.conf".format(self.box[0]),
                                          "sed -i 's/BOX_Y/{}/g' *.conf".format(self.box[1]),
                                          "sed -i 's/BOX_Z/{}/g' *.conf".format(self.box[2]),
                                          "sed -i 's/SYSTEM/{}/g' *.conf".format(system)]

                        task.pre_exec += ["sed -i 's/STEP/{}/g' *.conf".format(self.step_count[step])]

                        task.pre_exec += ["sed -i 's/LAMBDA/{}/g' *.conf".format(ld)]

                        stage.add_tasks(task)

            pipeline.add_stages(stage)

            # Analysis stage
            # ==============
            analysis = Stage()
            analysis.name = 'analysis'

        for replica in range(self.number_of_replicas):
            for system in self.systems:
                self.box = pmd.amber.AmberAsciiRestart('systems/ties{lig}/{s}/build/{s}-complex.crd'.format(lig=self.ligand, s=system)).box            
                analysis_task = Task()
                analysis_task.name = 'system_{}_replica_{}'.format(system,replica)

                analysis_task.arguments += ['-d', '*ti.out', '>', 'dg_{}.out'.format(analysis_task.name)]
                analysis_task.executable = [NAMD_TI_ANALYSIS]

                analysis_task.mpi = False
                analysis_task.cores = 1

                production_stage = pipeline.stages[-1]
                production_tasks = [t for t in production_stage.tasks if analysis_task.name in t.name]
                links = ['$Pipeline_{}_Stage_{}_Task_{}/alch_{}_ti.out'.format(pipeline.uid, production_stage.uid, t.uid, t.name.split('_lambda_')[-1]) for t in production_tasks]
                analysis_task.link_input_data = links

                analysis.add_tasks(analysis_task)

        pipeline.add_stages(analysis)

        # Averaging stage
        # ===============
        average = Stage()
        average.name = 'average'

        for system in self.systems:
            self.box = pmd.amber.AmberAsciiRestart('systems/ties{lig}/{s}/build/{s}-complex.crd'.format(lig=self.ligand, s=system)).box            

            average_task = Task()
            average_task.name = 'average_dg'
            average_task.arguments = ['-1 --quiet dg_* > dgs.out']  # .format(pipeline.uid)]
            average_task.executable = ['head']

            average_task.mpi = False
            average_task.cores = 1

            previous_stage = pipeline.stages[-1]
            previous_tasks = previous_stage.tasks


            links = ['$Pipeline_{}_Stage_{}_Task_{}/dg_{}.out'.format(pipeline.uid, previous_stage.uid, t.uid,
                                                                      t.name) for t in previous_tasks]
            average_task.link_input_data = links
            #average_task.download_output_data = ['dgs.out']  # .format(pipeline.uid)]

            average.add_tasks(average_task)
        pipeline.add_stages(average)

        print 'TIES pipeline has', len(pipeline.stages), 'stages. Tasks counts:', [len(s.tasks) for s in pipeline.stages]
        return pipeline

    # Input data
    @property
    def input_data(self):
        files = []
        for system in self.systems:
            files += ['default_configs/ties-{}.conf'.format(step) for step in self.workflow]
            files += ['systems/ties{lig}/{s}/build/{s}-complex.pdb'.format(lig=self.ligand, s=system)]
            files += ['systems/ties{lig}/{s}/build/{s}-complex.top'.format(lig=self.ligand, s=system)]
            files += ['systems/ties{lig}/{s}/build/{s}-tags.pdb'.format(lig=self.ligand, s=system)]
        print files
        return files

    

    @property
    def replicas(self):

        return self.number_of_replicas*len(self.lambdas)*self.instances

