#!/bin/bash
set -m
. /minecraft/parse_yaml.sh
eval $(parse_yaml /minecraft/host/config/server.yaml "config_")
CLIENTVERSION=$config_mcversion
VERSION=$config_mcversion
tobackup ()
{
    echo "Sending to backup"
    rsync -av --inplace --delete /minecraft/host/mcdata/world /minecraft/host/otherdata/mcbackup
}

fromram ()
{
    echo "Syncing ramdisk to disk"
    rsync -av /dev/shm/world /minecraft/host/mcdata    
}

function pipestart ()
{
    if [[ ! -p /minecraft/vanillabean ]]; then

        mkfifo /minecraft/vanillabean
    fi
    cat > /minecraft/vanillabean
}

mcstart ()
{
    trap mcstop INT

    cd /minecraft/host/mcdata

    if [[ ! -f minecraft_server.$VERSION.jar ]]; then

        wget -t inf https://s3.amazonaws.com/Minecraft.Download/versions/$VERSION/minecraft_server.$VERSION.jar
    
    fi
    
    if [[ ! -f $CLIENTVERSION.jar ]]; then
        wget -t inf https://s3.amazonaws.com/Minecraft.Download/versions/$CLIENTVERSION/$CLIENTVERSION.jar
    fi
    echo "Starting named pipe"
   ( pipestart ) &
    echo "Starting server"

    cp /minecraft/host/mcdata/world/data/villages.dat.bak /minecraft/host/mcdata/world/data/villages.dat
   ( /usr/bin/java -jar minecraft_server.$VERSION.jar nogui < /minecraft/vanillabean ) &
   PID=$!


    wait $PID
    echo "Server stopped"
    tobackup
}

mcstop ()
{
    /minecraft/vanillabean.py "/say server restarting in 10 seconds"
    sleep 10
    echo "/stop" > /minecraft/vanillabean
}



sync ()
{
    #echo "$(date) Sending sava-all to server"
    /minecraft/vanillabean.py "/save-off" 
    sleep 2
    /minecraft/vanillabean.py "/save-all" 

    sleep 10

    #echo "$(date) Syncing ramdisk with disk"
    tobackup
    #echo "$(date) Creating snapshot"
    # sudo zfs snapshot main/minecraft/world@$(date +%Y%m%d%H%M)

    sleep 10

    /minecraft/vanillabean.py "/save-on" 

    echo "$(date) sync done"
}

case $1 in
start)
mcstart
;;
stop)
mcstop
;;
sync)
sync
;;
esac
