from radical.htbac import Ties, Runner


def main():

    ht = Runner()

    ties1 = Ties(number_of_replicas=5, number_of_windows=11,
                 workflow=['min', 'eq1', 'eq2', 'prod'],
                 system='brd4-gsk3-1')

    ties2 = Ties(number_of_replicas=5, number_of_windows=11,
                 workflow=['min', 'eq1', 'eq2', 'prod'],
                 system='brd4-gsk3-1', ligand=True)

    ht.add_protocol(ties1)
    ht.add_protocol(ties2)
    ht.cores = 32
    ht.rabbitmq_config()
    ht.run(walltime=240, strong_scaled=0.5)


if __name__ == '__main__':
    import os

    os.environ['RADICAL_ENTK_VERBOSE'] = 'INFO'
    os.environ['RADICAL_PILOT_DBURL'] = 'mongodb://radical:fg*2GT3^eB@crick.chem.ucl.ac.uk:27017/admin'
    os.environ['RP_ENABLE_OLD_DEFINES'] = 'True'
    os.environ['SAGA_PTY_SSH_TIMEOUT'] = '2000'
    os.environ['RADICAL_PILOT_PROFILE'] = 'True'
    os.environ['RADICAL_ENMD_PROFILE'] = 'True'
    os.environ['RADICAL_ENMD_PROFILING'] = '1'

    main()
