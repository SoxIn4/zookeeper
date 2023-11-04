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


MANAGED_INSTALL_DIR = CFPreferencesCopyAppValue('ManagedInstallDir', 'ManagedInstalls')
if MANAGED_INSTALL_DIR is None:
    print('ERROR: Cannot get Managed Installs directory...')
    # sys.exit(1)

# Make sure a LocalOnlyManifest is specified, exit if not declared
MANIFEST = CFPreferencesCopyAppValue('LocalOnlyManifest', 'ManagedInstalls')
if MANIFEST is None:
    print("ERROR: No LocalOnlyManifest declared...")
    # sys.exit(1)

MANIFEST_PATH = f'{MANAGED_INSTALL_DIR}/manifests/{MANIFEST}'


def get_manifest():
    if os.path.exists(f'{MANAGED_INSTALL_DIR}/manifests/{MANIFEST}'):
        # If LocalOnlyManifest exists, try to read it
        try:
            return FoundationPlist.readPlist(f'{MANAGED_INSTALL_DIR}/manifests/{MANIFEST}')
        except FoundationPlist.NSPropertyListSerializationException:
            print(f'ERROR: Cannot read {MANAGED_INSTALL_DIR}/manifests/{MANIFEST}')
            sys.exit(1)

    return {}

def get_action():
    '''Check parameter 4 for section.action'''

    try:
        arg_4 = sys.argv[4]
    except IndexError:
        print('Parameter 4 not set, must provide section.action')
        sys.exit(4)

    if arg_4:
        try:
          section, action = arg_4.split('.')
        except ValueError:
            print('Parameter 4 must be in the form section.action.')
            sys.exit(4)

        actions = ['add', 'remove']
        if action not in actions:
            print(f'Action must be one of: {actions}.')
            sys.exit(4)

        sections = ['managed_installs', 'managed_uninstalls',
                    'optional_installs', 'managed_updates']
        if section not in sections:
            print(f'Section must be one of: {sections}.')
            sys.exit(4)

        return section, action

def get_action_items():
    '''Check parameter 5 and return a list of items to add or remove.'''

    try:
        items = sys.argv[5]
    except IndexError:
        print('Parameter 5 not set, must provide item(s)')
        sys.exit(5)

    # if not items:
    #     print('No items to act on.')
    #     sys.exit(5)

    return [item.strip() for item in items.split(',')]

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
    processed_items = None
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

    if processed_items:
        # Write to disk
        FoundationPlist.writePlist(new_manifest, MANIFEST_PATH)
    
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
    section, action = get_action()
    action_items = get_action_items()
    force_mode = check_forced()
    processed, skipped = update_client_manifest(section, action_items, action)

    result = {'processed': list(processed),
              'skipped': list(skipped)}

    run_managedsoftwareupdate(forced=force_mode)

    print(json.dumps(result))
