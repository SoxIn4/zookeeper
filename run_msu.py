#!/usr/local/munki/munki-python

import sys
sys.path.append("/usr/local/munki")
from munkilib import launchd

def get_run_type():
    '''Check parameter 4 for run_type'''

    run_types = ['auto', 'installonly']
    format_message = f'Parameter 4 must be one of: {run_types}.'
    try:
        run_type = sys.argv[4]
    except IndexError:
        print(f'Parameter 4 not set. {format_message}')
        sys.exit(4)
    if run_type not in run_types:
        print(f'{format_message}')
        sys.exit(4)
    return run_type

run_type = get_run_type()
print(f'Running: /usr/local/munki/managedsoftwareupdate" --{run_type}')
job = launchd.Job(
    ["/usr/local/munki/managedsoftwareupdate", f"--{run_type}"], cleanup_at_exit=False)
job.start()
