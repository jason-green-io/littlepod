#!/bin/bash

for file in $(jq -r '.[] | select(.Color | contains("black"))|.Filename' $WEBFOLDER/mca.json); do
    echo Deleting $DATAFOLDER/mc/world/$file
    rm $DATAFOLDER/mc/world/$file
done
