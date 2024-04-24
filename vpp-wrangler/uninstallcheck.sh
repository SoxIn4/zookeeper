#!/bin/zsh
app='/Applications/FindAndReplaceAllWithAppName.app'
if [[ ! -d $app ]]; then
	exit 1
fi

echo $app is installed, uninstalling
