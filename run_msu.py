#!/usr/local/munki/munki-python

import sys
sys.path.append("/usr/local/munki")
from munkilib import launchd

def get_runtype():
    '''Check parameter 4 for runtype'''

    runtypes = ['', 'auto']
    format_message = f'Parameter 4 must be one of: {runtypes}.'
    try:
        runtype = sys.argv[4]
    except IndexError:
        print(f'Parameter 4 not set. {format_message}')
        sys.exit(4)
    if runtype not in runtypes:
        print(f'{format_message}')
        sys.exit(4)

runtype = get_runtype()
job = launchd.Job(
    ["/usr/local/munki/managedsoftwareupdate", f"--{runtype}"], cleanup_at_exit=False)
job.start()
