# Version
from radical.htbac.version import version, __version__

from radical.htbac.htbac import Runner
from radical.htbac.esmacs import Esmacs
from radical.htbac.ties import Ties

import os

# Setting the environment variables so you don't have to.

os.environ['RADICAL_ENMD_PROFILING'] = '1'
os.environ['RADICAL_PILOT_PROFILE'] = 'True'
os.environ['RADICAL_ENMD_PROFILE'] = 'True'
os.environ['RADICAL_ENTK_VERBOSE'] = 'INFO'
os.environ['RADICAL_PILOT_DBURL'] = 'mongodb://htbac-user:password@ds131826.mlab.com:31826/htbac-isc-experiments'

os.environ['RP_ENABLE_OLD_DEFINES'] = 'True'
os.environ['SAGA_PTY_SSH_TIMEOUT'] = '2000'


