#!/bin/zsh

runType="$1"
echo "Runtype is: $runType"
if [[ $runType == "manualcheck" ]]; then
    echo "Check-only run, doing nothing"
else
    installReport="/Library/Managed Installs/ManagedInstallReport.plist"
    if [[ -f $installReport ]]; then
        installs="$(/usr/bin/defaults read "/Library/Managed Installs/ManagedInstallReport.plist" InstallResults)"
        removals="$(/usr/bin/defaults read "/Library/Managed Installs/ManagedInstallReport.plist" RemovalResults)"
        if [[ ${#installs[@]} == 3 ]] && [[ ${#removals[@]} == 3 ]]; then
            echo "No installs or removals, doing nothing."
        else
            echo "Running jamf recon"
            /usr/local/bin/jamf recon
        fi
    fi
fi
