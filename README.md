Zookeeper
=============

## Introduction

Zookeeper was heavily inspired by jamJar as an attempt to use the best parts of both tools. I'm writing this to use in a fresh jamf instance, so I have not considered at all how this might be added to a live environment. Besides being able to add or remove items from any valid section (`['managed_installs', 'managed_uninstalls', 'optional_installs', 'managed_updates']`) of a client's local manifest, zookeeper will not provide additional notification capabilities, and it encourages the use of Managed Software Center for users to install optional apps.

This will let us take full advantage of everything munki has to offer and reduce clutter in users' self help options by separating software installs in MSC from company resources and support in Self-Service.

## Usage

1. Copy the script to your jamf instance.
2. Set parameter labels
    1. Parameter 4: `Section.Action (Action must be *all* or *remove*)`
    2. Parameter 5: `Items (One or more separated by commas)`
    3. Parameter 11: `Force Mode`
4. Use in profiles!

# Work in progress
This is very experimental and untested. We're in the process of building a fresh jamf environment after being away for 10+ years. This script will evolve as we move on and learn more.

If you're crazy enough to want to try this out now, please reach out with feedback to SoxIn4 in the Mac Admins' Slack or post an issue here.
