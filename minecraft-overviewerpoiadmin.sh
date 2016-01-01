#!/bin/bash
. /minecraft/parse_yaml.sh

eval $(parse_yaml /minecraft/host/config/server.yaml "config_")
parse_yaml /minecraft/host/config/server.yaml config_

ADMIN=$config_webdata/map/$config_mapadminsecret
echo Removing $ADMIN

rm -r $ADMIN/*

mkdir $ADMIN

overviewer.py --skip-scan --config=/minecraft/host/config/overviewerconfigadmin.py --genpoi

for file in /minecraft/host/webdata/map/*; do
    ln -s $file $ADMIN
done
