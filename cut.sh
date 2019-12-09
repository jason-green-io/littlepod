#!/bin/bash

for file in $(jq -r '.[] | select(.Color | contains("black"))|.Filename'$WEBDATA/mca.json); do
    rm $DATAFOLDER/mc/world/$file
done
