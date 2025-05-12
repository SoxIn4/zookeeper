#!/usr/local/munki/munki-python
import os
import sys

sys.path.append('/usr/local/munki')
try:
    from munkilib import FoundationPlist
except ImportError:
    print('<result>ERROR: Cannot import FoundationPlist</result>')
    sys.exit(1)

managed_installs = "/Library/Managed Installs"
report_plist = f'{managed_installs}/ManagedInstallReport.plist'
highest_supported = None

if os.path.exists(report_plist):
    try:
        msu_report =  FoundationPlist.readPlist(report_plist)
    except FoundationPlist.NSPropertyListSerializationException:
        print(f'<result>ERROR: Cannot read {report_plist}</result>')
        sys.exit(1)

    monterey_supported = msu_report['Conditions']['monterey_upgrade_supported']
    ventura_supported = msu_report['Conditions']['ventura_upgrade_supported']
    sonoma_supported = msu_report['Conditions']['sonoma_upgrade_supported']
    sequoia_supported = msu_report['Conditions']['sequoia_upgrade_supported']

    if sequoia_supported:
        highest_supported = "Sequoia"
    elif sonoma_supported:
        highest_supported = "Sonoma"
    elif ventura_supported:
        highest_supported = "Ventura"
    elif monterey_supported:
        highest_supported = "Monterey"

if not highest_supported:
    highest_supported = "No valid Upgrades available"

print(f'<result>{highest_supported}</result>')
