#!/usr/local/munki/munki-python
# encoding: utf-8
'''
This script was heavily inspired by jamJAR. While a few dozen or so lines were coppied
directly from it, the intention is very different. This script has no notification
capabilities and can add or remove items from any valid section of a local munki client
manifest.

It is highly experimental, and not used in production. (yet?)
Use at your own risk. 
'''


__version__ = '0.1'


import json
import os
import subprocess
import sys
from CoreFoundation import CFPreferencesCopyAppValue

sys.path.append("/usr/local/munki")
try:
    from munkilib import FoundationPlist
except ImportError:
    print('ERROR: Cannot import FoundationPlist')
    sys.exit(1)


FORMAT = '{section: {action1: ["app", "list"], action2: ["app"]}}'
SECTIONS = ['managed_installs', 'managed_uninstalls',
            'optional_installs', 'managed_updates']
ACTIONS = ['add', 'remove']

MANAGED_INSTALL_DIR = CFPreferencesCopyAppValue('ManagedInstallDir', 'ManagedInstalls')
if MANAGED_INSTALL_DIR is None:
    print('ERROR: Cannot get Managed Installs directory...')
    sys.exit(1)

# Make sure a LocalOnlyManifest is specified, exit if not declared
MANIFEST = CFPreferencesCopyAppValue('LocalOnlyManifest', 'ManagedInstalls')
if MANIFEST is None:
    print("ERROR: No LocalOnlyManifest declared...")
    sys.exit(1)

MANIFEST_PATH = f'{MANAGED_INSTALL_DIR}/manifests/{MANIFEST}'
# MANAGED_INSTALL_DIR = '/Library/Managed Installs'
# MANIFEST = 'LocalOnlyManifest'
# MANIFEST_PATH = f'/Library/Managed Installs/manifests/LocalOnlyManifest'


def get_manifest():
    if os.path.exists(f'{MANAGED_INSTALL_DIR}/manifests/{MANIFEST}'):
        # If LocalOnlyManifest exists, try to read it
        try:
            return FoundationPlist.readPlist(f'{MANAGED_INSTALL_DIR}/manifests/{MANIFEST}')
        except FoundationPlist.NSPropertyListSerializationException:
            print(f'ERROR: Cannot read {MANAGED_INSTALL_DIR}/manifests/{MANIFEST}')
            sys.exit(1)

    return {}

def get_commands():
    '''
    Check parameters 4-10 for
    {section: {action1: ["app", "list"], action2: ["app"]}}
    '''

    commands = []
    for arg in sys.argv[4:11]:
        if arg:
            try:
                command = json.loads(arg)
                try:
                    if len(command) != 1:
                        print(f'Command: "{command}" not formatted correctly.\n'
                              'Must have 1 section with at least 1 action '
                              'with a list with at least 1 app.\n'
                              f'Expected format: {FORMAT}')
                        sys.exit(1)
                except TypeError as error:
                    print(f'{command_error}\n{error}')
                    sys.exit(1)
                section = list(command.keys())[0]
                if section not in SECTIONS:
                    print(f'{section} not a valid section.\n'
                          'Section must be one of: {SECTIONS}.\n'
                          f'Expected format: {FORMAT}')
                    sys.exit(1)
                commands.append(command)

            except json.decoder.JSONDecodeError as error:
                print(f'Arg: {arg} not formatted correctly.\n'
                      f'Expected format: {FORMAT}\n{error}')
                sys.exit(1)
    return commands

def check_forced():
    '''Check if parameter 11 is set to 'ENGAGE' and return boolean.'''

    force_mode = False
    try:
        force_mode = sys.argv[11]
    except IndexError:
        pass

    if force_mode == 'ENGAGE':
        print("WARNING: Forced mode engaged")
        return True
    return False

def update_client_manifest(section, items, action):
    '''
        Perform the <action> on the <items> in the <section> of the LocalOnlyManifest.
        Writes the new manifest to disk and returns two lists: processed_items, skipped_items
    '''

    original_manifest = get_manifest()
    original_manifest_items = set(original_manifest.get(section, []))
    action_items = set(items)
    unique_items = action_items - original_manifest_items
    common_items = action_items.intersection(original_manifest_items)

    new_manifest = dict(original_manifest)
    processed_items, skipped_items = None, None
   
    match action:
        case 'add':
            skipped_items = common_items
            if unique_items:
                # combine items
                new_manifest_items = original_manifest_items.union(unique_items)
                new_manifest[section] = list(new_manifest_items)
                processed_items = unique_items
            else:
                print(f'Nothing to add. {items} already in {section}')
        case 'remove':
            skipped_items = unique_items
            if common_items:
                # remove items
                new_manifest_items = original_manifest_items - common_items
                new_manifest[section] = list(new_manifest_items)
                processed_items = common_items
            else:
                print(f'Nothing to remove. {items} not in {section}')
        case '*':
            print(f'Action must be one of: {ACTIONS}.')
            sys.exit(4)

    if processed_items:
        # Write to disk
        FoundationPlist.writePlist(new_manifest, MANIFEST_PATH)
        processed_items = list(processed_items)
    if skipped_items:
        skipped_items = list(skipped_items)
    return processed_items or [], skipped_items or []

def run_managedsoftwareupdate(forced=None):
    '''
        Default: Run managedsoftwareupdate --auto -m
        If forced == True, run 'managedsoftwareupdate --checkonly'
                           followed by 'managedsoftwareupdate --installonly'
    '''
    msu = ['/usr/local/munki/managedsoftwareupdate']
    args_sets = [['--auto', '-m']] if not forced else [['--checkonly'], ['--installonly']]

    for args in args_sets:
        cmd = msu + args
        try:
            subprocess.call((cmd), stdout=subprocess.DEVNULL)
        except subprocess.CalledProcessError as err_msg:
            print(f"ERROR: {cmd} failed with: ", err_msg)
            sys.exit(1)


if __name__ == "__main__":
    # Make sure we're root
    if os.geteuid() != 0:
        print('ERROR: This script must be run as root')
        sys.exit(1)

    # Process the parameters
    force_mode = check_forced()
    commands = get_commands()

    result = {}
    for command in commands:
        section = list(command.keys())[0]
        actions = list(command[section].keys())
        for action in actions:
            action_items = command[section][action]
            print(f'{section}-{action}-{action_items}')
            processed, skipped = update_client_manifest(section, action_items, action)
            print(f'Processed: {processed}, Skipped: {skipped}')
            new_section = result.get(section, {})
            if processed:
                existing = new_section.get(action, [])
                new_section[action] = existing + processed
            if skipped:
                existing = new_section.get('skipped', [])
                new_section['skipped'] = existing + skipped
            result[section] = new_section

    run_managedsoftwareupdate(forced=force_mode)

    print(json.dumps(result))
