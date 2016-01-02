#!/bin/bash
. /minecraft/parse_yaml.sh

eval $(parse_yaml /minecraft/host/config/server.yaml "config_")
parse_yaml /minecraft/host/config/server.yaml config_

if [[ $1 == "yesterday" ]]; then
    yesterday=$(date -d @$(($(date +%s) - 24 * 3600)) +%Y%m%d)
    ADMIN=$config_webdata/map/$config_mapadminsecret/$yesterday
    mkdir $ADMIN

    overviewer.py --skip-scan --config=/minecraft/host/config/overviewerconfigadmin.py --genpoi yesterday

    for file in /minecraft/host/webdata/map/*; do
        ln -s $file $ADMIN
    done
else
    ADMIN=$config_webdata/map/$config_mapadminsecret/latest
    echo Removing $ADMIN

    rm -r $ADMIN/latest/*

    mkdir $ADMIN/latest

    overviewer.py --skip-scan --config=/minecraft/host/config/overviewerconfigadmin.py --genpoi

    for file in /minecraft/host/webdata/map/*; do
        ln -s $file $ADMIN
    done
fi
