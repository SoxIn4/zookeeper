#!/usr/local/munki/munki-python
import os
import sys

sys.path.append('/usr/local/munki')
try:
    from munkilib import FoundationPlist
except ImportError:
    print('ERROR: Cannot import FoundationPlist')
    sys.exit(1)


trigger_list_dir = '/usr/local/matw/config'
trigger_list_name = 'profile_triggers'
trigger_list_path = f'{trigger_list_dir}/{trigger_list_name}.plist'
triggers = None

if os.path.exists(trigger_list_path):
    try:
        triggers_plist =  FoundationPlist.readPlist(trigger_list_path)
    except FoundationPlist.NSPropertyListSerializationException:
        print(f'ERROR: Cannot read {trigger_list_path}')
        sys.exit(1)

    triggers = triggers_plist['triggers']
    # if apps:
    #     print(f'<result>{apps}</result>')
    #     sys.exit(0)

print(f'<result>{list(triggers)}</result>')
