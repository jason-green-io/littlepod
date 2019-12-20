#!/bin/bash

for file in $(jq -r '.[] | select(.Color | contains("black"))|.Filename' $WEBDATA/mca.json); do
    echo Deleting $DATAFOLDER/mc/world/$file
    rm $DATAFOLDER/mc/world/$file
done
