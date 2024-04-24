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
vpp_apps_plist = None

if os.path.exists(vpp_list_path):
    try:
        vpp_apps_plist =  FoundationPlist.readPlist(vpp_list_path)
        if target in vpp_apps_plist['apps']:
            print(f'{target} is already in the vpp list, nothing to do')
            sys.exit(0)
        else:
            vpp_apps_plist['apps'].append(target)
    except FoundationPlist.NSPropertyListSerializationException:
        print(f'ERROR: Cannot read {vpp_list_path}')
        sys.exit(1)

if not vpp_apps_plist:
    vpp_apps_plist = {'apps': [target]}

if not os.path.exists(vpp_list_dir):
    os.makedirs(vpp_list_dir)
FoundationPlist.writePlist(vpp_apps_plist, vpp_list_path)
print(f'{target} added to vpp list at {vpp_list_path}')
