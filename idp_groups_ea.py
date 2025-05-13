#!/usr/local/munki/munki-python
import os
import sys

sys.path.append('/usr/local/munki')
try:
    from munkilib import FoundationPlist
except ImportError:
    print('ERROR: Cannot import FoundationPlist')
    sys.exit(1)

# Edit path for your environment
group_list_dir = '/usr/local/zookeeper/config'

# Edit name of file with idp_groups
group_list_name = 'groups'
group_list_path = f'{group_list_dir}/{group_list_name}.plist'
groups = None

if os.path.exists(group_list_path):
    try:
        group_plist =  FoundationPlist.readPlist(group_list_path)
    except FoundationPlist.NSPropertyListSerializationException:
        print(f'ERROR: Cannot read {group_list_path}')
        sys.exit(1)

    groups = group_plist['idp_groups']

print(f'<result>{list(groups)}</result>')
