#!/bin/bash

CLIENTVERSION=1.8.9
tobackup ()
{
    echo "Sending to backup"
    rsync -av /minecraft/host/mcdata/world /minecraft/host/otherdata/mcbackup
}

fromram ()
{
    echo "Syncing ramdisk to disk"
    rsync -av /dev/shm/world /minecraft/host/mcdata    
}

mcstart ()
{

    VERSION=$(cat /minecraft/host/config/mcversion)

    cd /minecraft/host/mcdata

    if [[ ! -f minecraft_server.$VERSION.jar ]]; then

        wget -t inf https://s3.amazonaws.com/Minecraft.Download/versions/$VERSION/minecraft_server.$VERSION.jar
    
    fi
    
    if [[ ! -f $CLIENTVERSION.jar ]]; then
        wget -t inf https://s3.amazonaws.com/Minecraft.Download/versions/$CLIENTVERSION/$CLIENTVERSION.jar
    fi
    /usr/bin/tmux neww -t minecraft:7 "/usr/bin/java -jar minecraft_server.$VERSION.jar nogui"
}

mcstop ()
{

    /minecraft/vanillabean.py "/stop"
    sleep 5
    tobackup
}

mcrestart ()
{

    /minecraft/vanillabean.py "/say server restarting in 30 seconds"
    sleep 30
    #/minecraft/minecraft-sync.sh &>> /minecraft/minecraft-sync.log
    mcstop
    sleep 10
    mcstart
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
restart)
mcrestart
;;
stop)
mcstop
;;
sync)
sync
;;
esac
