#!/bin/bash

if [[ -z $1 ]]; then
	echo "Provide rm, echo or something"
	exit
fi

for file in $(jq -r '.[] | select(.properties.protected == false) | .properties.filename' $WEBFOLDER/custom.json); do
    $1 $DATAFOLDER/mc/world/$file
done
