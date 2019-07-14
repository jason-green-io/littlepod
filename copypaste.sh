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

        rsync -aP $DATAFOLDER/mc/world $DATAFOLDER/backup
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

        rsync -aP $DATAFOLDER/bds/worlds $DATAFOLDER/backup
        rm $DATAFOLDER/backup/world/db/LOCK
        sleep 10
        {
        echo "save resume"
        sleep 1
        } | ncat localhost 7777

    ;;
esac
echo $(date) "Backup done"
