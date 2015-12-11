#! /bin/bash
toram ()
{
    rsync -av /minecraft/host/mcdata/* /dev/shm/world 
}

fromram ()
{
    rsync -av /dev/shm/world/* /minecraft/host/mcdata    
}

mcstart ()
{

    VERSION=$(cat /minecraft/host/config/mcversion)

    cd /minecraft/host/mcdata

    if [[ ! -f minecraft_server.$VERSION.jar ]]; then

        wget -t inf https://s3.amazonaws.com/Minecraft.Download/versions/$VERSION/minecraft_server.$VERSION.jar
    fi

    tmux neww -t minecraft:7 "java -jar minecraft_server.$VERSION.jar nogui"
}

mcstop ()
{

    /minecraft/vanillabean.py "/stop"
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
    /minecraft/vanillabean.py "/save-all" 

    sleep 10

    #echo "$(date) Syncing ramdisk with disk"
    fromram
    echo "$(date) Creating snapshot"
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
esac
