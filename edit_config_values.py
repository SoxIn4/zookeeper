#!/usr/local/munki/munki-python
import json
import os
import sys

sys.path.append('/usr/local/munki')
try:
    from munkilib import FoundationPlist
except ImportError:
    print('ERROR: Cannot import FoundationPlist')
    sys.exit(1)

# Set a path to store the plists
CONFGDIR = '/usr/local/company_name/config'

# Edit this to reflect your needs
FILES = {'groups': {'sections': ['idp_groups', 'jamf_groups']},
         'tags': {'sections': ['device_tags', 'user_tags']}}

if not os.path.exists(CONFGDIR):
    os.makedirs(CONFGDIR)

def get_command():
    '''Check parameter 4 for file.section.action'''

    format_message = 'Parameter 4 must be in the form file.section.action.'
    try:
        arg_4 = sys.argv[4]
    except IndexError:
        print(f'Parameter 4 not set. {format_message}')
        sys.exit(4)

    try:
        file, section, action = arg_4.split('.')
    except ValueError:
        print(f'{format_message}')
        sys.exit(4)

    # filename = f'{file}.plist'
    if f'{file}' not in FILES:
        print(f'Invalid file. Must be one of: {list(FILES.keys())}.')
        sys.exit(4)
    errors = []
    sections = FILES[file]['sections']
    if section not in sections:
        errors.append(f'Section must be one of: {sections}.')

    actions = ['add', 'remove']
    if action not in actions:
        errors.append(f'Action must be one of: {actions}.')

    if errors:
        message = "\n".join(errors)
        print(f'{message}\n')
        sys.exit(4)

    return f'{file}.plist', section, action

def get_action_items():
    '''Check parameter 5 and return a list of items to add or remove.'''

    try:
        items = sys.argv[5]
    except IndexError:
        print('Parameter 5 not set, must provide item(s)')
        sys.exit(5)
    return [item.strip() for item in items.split(',')]

def get_plist(file):
    if os.path.exists(f'{file}'):
        # If LocalOnlyManifest exists, try to read it
        try:
            return FoundationPlist.readPlist(f'{file}')
        except FoundationPlist.NSPropertyListSerializationException:
            print(f'ERROR: Cannot read {file}')
            sys.exit(1)

    return {}

def update_plist(filename, section, items, action):
    '''
        Perform the <action> on the <items> in the <section> of the LocalOnlyManifest.
        Writes the new manifest to disk
        Returns two lists: processed_items, skipped_items
    '''

    plist_file = f'{CONFGDIR}/{filename}'
    original_plist = get_plist(plist_file)
    original_plist_items = set(original_plist.get(section, []))
    action_items = set(items)
    unique_items = action_items - original_plist_items
    common_items = action_items.intersection(original_plist_items)

    new_plist = dict(original_plist)
    processed_items = None
    match action:
        case 'add':
            skipped_items = common_items
            if unique_items:
                # combine items
                new_plist_items = original_plist_items.union(unique_items)
                new_plist[section] = list(new_plist_items)
                processed_items = unique_items
            else:
                print(f'Nothing to add. {items} already in {section}')
        case 'remove':
            skipped_items = unique_items
            if common_items:
                # remove items
                new_plist_items = original_plist_items - common_items
                new_plist[section] = list(new_plist_items)
                processed_items = common_items
            else:
                print(f'Nothing to remove. {items} not in {section} in {plist_file}')

    if processed_items:
        # Write to disk
        FoundationPlist.writePlist(new_plist, f'{plist_file}')
        list(processed_items)
    
    return processed_items or [], list(skipped_items) or []


if __name__ == "__main__":
    # Make sure we're root
    if os.geteuid() != 0:
        print('ERROR: This script must be run as root')
        sys.exit(1)
    # Process the parameters
    filename, section, action = get_command()
    action_items = get_action_items()

    # execute actions
    processed, skipped = update_plist(filename, section, action_items, action)

    result = {'processed': list(processed),
              'skipped': list(skipped)}

    # run_managedsoftwareupdate(forced=force_mode)

    print(json.dumps(result))
