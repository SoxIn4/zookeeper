'''Return a list of entra groups for the JAMF enrolled user'''

from __future__ import absolute_import, print_function

import os
import sys

sys.path.append('/usr/local/munki')
try:
    from munkilib import FoundationPlist
except ImportError:
    print('ERROR: Cannot import FoundationPlist')
    sys.exit(1)

# Edit path for your environment
group_list_dir = '/usr/local/company_name/config'

def fact():
    '''Return the list of entra groups for the JAMF enrolled user'''
    return {'idp_groups': get_idp_groups()}

def get_idp_groups():
    """Read groups from /usr/local/matw/config/groups.plist."""
    group_list_name = 'groups'
    group_list_path = f'{group_list_dir}/{group_list_name}.plist'

    if os.path.exists(group_list_path):
        try:
            groups_plist =  FoundationPlist.readPlist(group_list_path)
        except FoundationPlist.NSPropertyListSerializationException:
            print(f'ERROR: Cannot read {group_list_path}')
            sys.exit(1)

        idp_groups = groups_plist['idp_groups']
        return(idp_groups)

    return([])


if __name__ == '__main__':
    print(fact())
