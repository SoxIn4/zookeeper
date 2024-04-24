#!/bin/zsh

userName=$(defaults read "/Library/Managed Preferences/com.company_name.automation.info.plist" jamf_enrolled_user)
echo "Running policies for user: $userName"
/usr/local/bin/jamf policy -event asUser -username $userName

exit 0
