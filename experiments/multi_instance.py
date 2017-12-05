from radical.htbac import Ties, Esmacs, Runner


def main():

    ht = Runner()

    ties3_1 = Ties(number_of_replicas=2, number_of_windows=3,
                   workflow=['min', 'eq1', 'eq2', 'prod'],
                   system='brd4-gsk3-1')

    esmacs1 = Esmacs(number_of_replicas=5,
                     system='brd4-gsk1',
                     workflow=['eq0', 'eq1', 'eq2', 'sim1'])

    ht.add_protocol(ties3_1)
    ht.add_protocol(esmacs1)
    ht.cores = 32
    ht.rabbitmq_config()
    ht.run()


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