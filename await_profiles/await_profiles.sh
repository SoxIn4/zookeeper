#!/bin/zsh

# Usage: await_profiles.sh <profile_name1> <profile_name2> ... <profile_nameN> <LD_to_delete>"

# # Check if at least one profile name and a file to delete are provided
# if [ "$#" -lt 2 ]; then
#     echo "Usage: $0 <profile_name1> <profile_name2> ... <profile_nameN> <LD_to_delete>"
#     exit 1
# fi

ld_path='/Library/LaunchDaemons'

ld_label="${@:$#}"
file_to_delete="$ld_path/$ld_label.plist"

# Store the profile names from the command-line arguments, excluding the last one
profile_names=("${@:1:-1}")

echo "$(date)  Profile names: ${(j:, :)profile_names}"
# Function to check if all specified configuration profiles are installed
profiles_are_installed() {
    for profile in "${profile_names[@]}"; do
        if ! profiles list -verbose | grep -q "attribute: name: $profile"; then
            echo "$(date)  $profile NOT FOUND"
            return 1  # Return 1 if any profile is not found
        fi
        echo "$(date)  FOUND $profile"
    done
    echo "$(date)  All profiles found"
    return 0  # Return 0 if all profiles are found
}

# Main loop
while true; do
    if profiles_are_installed; then
        # Run msu detached so it won't get killed when the job unloads
        echo "$(date)  All specified profiles are installed. Running managedsoftwareupdate..."
        /usr/local/munki/managedsoftwareupdate --auto &

        # Delete the specified file if it exists
        if [ -f "$file_to_delete" ]; then
            echo "$(date)  Deleting LD: $file_to_delete"
            rm "$file_to_delete"
            echo "$(date)  Unloading file from launchd: $file_to_delete"
            launchctl bootout system/"$ld_label"
        else
            echo "$(date)  File not found: $file_to_delete"
        fi

        # Exit the loop after running the command and deleting the file
        break
    fi
    # Sleep for a specified interval before checking again
    sleep 4
done
