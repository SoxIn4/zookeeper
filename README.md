# Zookeeper

A framework for integrating Jamf and Munki

Zookeeper is a small set of scripts and a munki pkginfo template to help integrate Munki and Jamf. Basically they let you use information (like a user's IDP group membership) from Jamf as conditions in Munki manifests.
They make it easier to start using munki on a large scale without needing to consider how to potentially manage thousands of individual device manifests up front. Each piece is useful on its own, but together, they make it easy to offload all software installs to Munki, while still being able to use Jamf static and smart group membership to control what a device gets. In a large environment, this helps keep users' self service options cleaner, with all software installs (including optional VPP apps) and updates done through Munki's MSC, and all other supprt related tasks in Jamf SS.

## Usage

- This assumes you have a working munki environment!
- Unless you want to write your own munki conditions, munki-facts is required

### munki_postflight_recon.sh

This must be installed on your clients as a munki postflight script.
While most of the stuff int his repo can work independently of one another, almost everything here depends on the postflight script.
If you're already using a postflight sctipt that runs scripts from a postflight.d dir, you can drom the recon.sh script in there. If you don't have a postinstall script, use the one provided.
(both scripts afre identical)
It will run a jamf recon whenever munki has installed or removed anything to keep jamf up to date.

### edit_config_values.py

This is probably the most useful script here. Combined with munki_postflight_recon, it opens a lot of possibilities. It was written initially to support IDP groups, but quickly evolved to serve more use cases. It basically just writes values to plists, and functions very similarly to the zookeeper.py script.

Setup script in Jamf:

1. Copy the script to your jamf instance.
2. Edit Lines 13 and 17 to fit `CONFIGDIR` and `FILES` to your environment and needs
3. Set parameter labels
    1. Parameter 4: `File.Section.Action (Action must be *add* or *remove*)`
    2. Parameter 5: `Value (One or more separated by commas)`

Use in profiles:

1. Add edit_config_values script to a profile
2. In parameter 4, add the file, section, and action. Example: `tags.device_tags.add`
3. In parameter 5 add the value(s). Example: `Tag1, Tag 2, Tag_3`

### vpp-wrangler

All of the scripts here except the ea script are part of the VPP_TEMPLATE.plist.
You can use the template to creat pkginfo files for vpp apps to be offered in MSC and delivered via VPP. Basically, when a user chooses to install a vpp app in MSC, munki will write the app name to a plist. Jamf will read the list of vpp apps into an ea, which is used to create smartgroups scoped to deploy the app.

Jamf setup:

1. Create a new EA with vpp_triggers_ea.py
2. Copy the display name of an App Store app from the Mac Apps section of your console
3. Create a smart group with the criteria: vpp_triggers like `app dispplay name`
4. Scope the app to the smart group and set it to automatically deploy.

Munki setup:

1. Duplicate and rename VPP_TEMPLATE.plist
2. Find and replace all occurrences of `APPNAME` with the app's display name you copied from Jamf above.
3. Find and edit all instances of `vpp_list_dir = '/usr/local/company_name/config'`
4. Edit the name key in line 21
5. Add a catalog(s) at line 19 if needed
6. Import the new pkginfo file to your munki repo
7. Using the name from step 3, add it to `optional_installs` or `default_installs` in mainfests in your repo, or use zookeeper.py to add it to local manifests.

### Use IDP Groups as Munki Conditions

Using IDP group memberships as conditions in Munki requires:

- an EA to list groups currently assigned to a device
- a smartgroup for each group based on the EA
- two policies using the edit_config_values script for each IDP group you want to use
- a fact for munki-facts to read the groups for conditions

If your users' local user accounts don't match their IDP usernames, you'll also need:

- a profile to make the Jamf enrolled username available on the devices
- a script to use that username to run jamf policies as that user
- a policy to run the script on each check-in

```text
Requires munki-facts:

Install munki-facts on your clients with idp_groups_fact.py in their munki-facts facts directory.
```

#### Jamf

1. Create a new EA with idp_groups_ea.py
    1. Suggested name: `IDP Groups`
    2. Edit `group_list_dir` at line 13
2. Make EA smart group
    1. Name: `IDP Groups - <paste_group_name>`
    2. Criteria: `IDP Groups like <paste_group_name>`
3. Make Write group name policy
    1. Name: `Add Group - <paste_group_name>`
    2. Trigger
        - If local and IDP usernames match: Recurring Check-in
        - If local and IDP usernames __don't__ match: Custom - `asUser`*
    3. Frequency: Ongoing
    4. Add script: Edit Config Values
        1. File.Section.Action: `groups.idp_groups.add`
        2. Items: `<paste_group_name>`
    5. Scope
        1. Target All Computers, Specific Users
        2. Limitations
            1. Add Directory Service Group
            2. <paste_group_name> in search field
            3. Select correct group and click done
        3. Exclusions
            1. Add smart group created in step 2
    6. Add Maintenance - Update Inventory
4. Make Removal policy
    1. Name: `Remove Group - <paste_group_name>`
    2. Trigger
        - If local and IDP usernames match: Recurring Check-in
        - If local and IDP usernames __don't__ match: Custom - `asUser`*
    3. Frequency: Ongoing
    4. Add script: Edit Config Values
        1. File.Section.Action: `groups.idp_groups.remove`
        2. Items: `<paste_group_name>`
    5. Scope
        1. Target Specific Computers, All Users
            1. Add smart group created in step 2
        2. Limitations - None
        3. Exclusions
            1. Add Directory Service Group
            2. <paste_group_name> in search field
            3. Select correct group and click done
    6. Add Maintenance - Update Inventory

#### Munki

Use group membership as a condition in munki manifests for items or manifests.

##### Condition syntax

assuming group names: HR-region 1, HR region 2, HR Global

to target a single group: `idp_groups CONTAINS "HR-region 1"`

to target all three: `ANY idp_groups CONTAINS "HR"`

theoretically, to target the two reginal groups: `ANY idp_groups LIKE "HR*region"` (I'm not positive this is correct, but I think it's close.)

#### * If your IDP and local usernames don't match

```text
For this to work, the enrolled users usernames on your devices in the Jamf console must be coming from your IDP or at least match the IDP usernames
```

1. Deploy a profile with the Jamf Username
    1. Name: `Company_Name Automation Data` (you may want to add properties to this for other uses, and if you have a similar profile already, you can use that instead.)
    2. Add External Application Payload
        1. Preference domain: `com.company_name.automation.info`
        2. Add custom schema:

        ```json
        {
            "title": "Automation Data",
            "description": "",
            "properties": {
                "jamf_enrolled_user": {
                "title": "Username",
                "description": "The Jamf device owner",
                "property_order": 10,
                "type": "string"
                }
            }
        }
        ```

    3. Under PreferenceDomain Properties enter `$USERNAME` in the Username field
2. Add `run_asUser.sh` into Jamf scripts
    1. Suggested name: `Run asUser Policies as Enrolled User`
    2. Edit the preference domain in line 3

    ```text
    This script will run on every check-in and run `jamf policy -event asUser -username` with the username in the profile to run the policies with the asUSer custom event trigger
    ```

3. Create Policy
    1. Name `Run Jamf Policies As Enrolled User`
    2. Trigger
        - Recurring Check-in
        - Optionally: Login and Custom - `runAsUser`
    3. Frequency: Ongoing

### Zookeeper.py

This is an easy way to get started using Munki with Jamf, especially if you've just setup your first munki repo. You can get started with this without setting up any manifests in your munki repo (you will need installers, and catalogs though).

Zookeeper's basic function is to add or remove items from any valid section (`['managed_installs', 'managed_uninstalls', 'optional_installs', 'managed_updates']`) of a client's local manifest.

With the other tools below, we've mostly stopped relying on this script altogether, but it was an essential stepping stone to help figure out how to fit both tools into our environment and get the most out of them. It let us start with a single unimportant app to get a feel for things before we moved to a manifest based approach leveraging a single standard manifest for most of our fleet with a lot of conditional included manifests that fuction very similarly to smart groups. It's still a good script to keep around to use in a pinch.

Setup script in Jamf:

1. Copy the script to your jamf instance.
2. Set parameter labels
    1. Parameter 4: `Section.Action (Action must be *add* or *remove*)`
    2. Parameter 5: `Items (One or more separated by commas)`
    3. Parameter 11: `Force Mode`

Use in profiles:

1. Add zookeeper script to a profile
2. In parameter 4, add the manifests section and action. Example: `managed_installs.add`
3. In parameter 5 add the name of the item(s) exactly as it appears in the name key in its pkginfo file.

## Background

This project started as an attempt to use the best parts of Munki and Jamf and originally focused on a script to use in Jamf policies to manage items in a device's local manifest in a very similar manner to JamJar, but with slightly different intentions. The original goal was basically to use Munki for all software installs without server-side manifests, controling everything via local manifests managed by Jamf. After some R&D, and some helpful guidance from the MacAdmin's Slack munki channel, ignoring server-side manifests turned out to be a huge mistake, so the project pivoted to these new tools to make it easy to expose data from jamf to munki for conditional items and manifests.

This let's you take full advantage of everything munki has to offer and reduce clutter in users' self help options by separating software installs in MSC from company resources and support in Self-Service.

## Work in progress

While this is all working well to support over 4000 live devices, and we've covered all of our immediate needs, we know there's plenty of room for improvement, and welcome any ideas or critiques!
