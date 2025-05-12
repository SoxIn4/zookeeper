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

if os.path.exists(report_plist):
    try:
        msu_report =  FoundationPlist.readPlist(report_plist)
    except FoundationPlist.NSPropertyListSerializationException:
        print(f'<result>ERROR: Cannot read {report_plist}</result>')
        sys.exit(1)

    msu_errors = msu_report['Errors']
else:
    msu_errors = 'No Report Available'

print(f'<result>{msu_errors or 'No Errors'}</result>')
