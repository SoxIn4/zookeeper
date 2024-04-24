#!/usr/local/munki/munki-python
import os
import sys

sys.path.append('/usr/local/munki')
try:
    from munkilib import FoundationPlist
except ImportError:
    print('ERROR: Cannot import FoundationPlist')
    sys.exit(1)


# Replace all instances of FindAndReplaceAllWithAppName with the app name
# Copy from your MDM or get the name as it appears on disk, minus ".app"
target = 'FindAndReplaceAllWithAppName'


# Edit path for your environment
vpp_list_dir = '/usr/local/company_name/config'
vpp_list_path = f'{vpp_list_dir}/vpp_apps.plist'

if os.path.exists(vpp_list_path):
    try:
        vpp_apps_plist =  FoundationPlist.readPlist(vpp_list_path)
    except FoundationPlist.NSPropertyListSerializationException:
        print(f'ERROR: Cannot read {vpp_list_path}')
        sys.exit(1)

    if target in vpp_apps_plist['apps']:
        vpp_apps_plist['apps'].remove(target)
        FoundationPlist.writePlist(vpp_apps_plist, vpp_list_path)
        print(f'{target} removed from {vpp_list_path}')
        sys.exit(0)
   
print(f'{target} not in {vpp_list_path}, nothing to do')
