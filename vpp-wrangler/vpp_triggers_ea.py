#!/usr/local/munki/munki-python
import os
import sys

sys.path.append('/usr/local/munki')
try:
    from munkilib import FoundationPlist
except ImportError:
    print('ERROR: Cannot import FoundationPlist')
    sys.exit(1)


vpp_list_dir = '/usr/local/zookeeper/config'
vpp_list_name = 'vpp_apps'
vpp_list_path = f'{vpp_list_dir}/{vpp_list_name}.plist'
apps = None

if os.path.exists(vpp_list_path):
    try:
        vpp_apps_plist =  FoundationPlist.readPlist(vpp_list_path)
    except FoundationPlist.NSPropertyListSerializationException:
        print(f'ERROR: Cannot read {vpp_list_path}')
        sys.exit(1)

    apps = vpp_apps_plist['apps']

print(f'<result>{list(apps)}</result>')
