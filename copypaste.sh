#!/bin/bash
echo $(date) "Starting backup"

case $TYPE in
    mc)
        {
        echo "/save-off"
        sleep 2
        echo "/save-all flush"
        sleep 10
        } | ncat localhost 7777

        echo $(date) "Syncing world to backup"

        restic --no-cache backup $DATAFOLDER/mc/world
        sleep 10
        {
        echo "/save-on"
        sleep 1
        } | ncat localhost 7777
        echo $(date) "sync done"
        #cut.py $SAVEMCA
    ;;
    bds)
        {
        echo "save hold"
        sleep 10
        } | ncat localhost 7777

        echo $(date) "Syncing world to backup"

        restic --no-cache backup $DATAFOLDER/bds/worlds
        sleep 10
        {
        echo "save resume"
        sleep 1
        } | ncat localhost 7777

    ;;
echo $(date) "Backup done"
esac
