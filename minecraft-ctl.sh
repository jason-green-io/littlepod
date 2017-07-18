#!/bin/bash
set -m
. /minecraft/parse_yaml.sh
eval $(parse_yaml /minecraft/host/config/server.yaml "config_")
CLIENTVERSION=$config_mcversion
VERSION=$config_mcversion
CONTROL="/minecraft/vanillabean"

case "$1" in
send)

    if kill -0 $(cat /minecraft/minecraft-ctl.sh.pid) > /dev/null 2&>1; then
       echo $2 >> $CONTROL
    else
	echo Not sent: $2
    fi
;;


start)



    cd /minecraft/host/mcdata

    if [[ ! -f minecraft_server.$VERSION.jar ]]; then

        wget -t inf https://s3.amazonaws.com/Minecraft.Download/versions/$VERSION/minecraft_server.$VERSION.jar
    
    fi
    
    if [[ ! -f $CLIENTVERSION.jar ]]; then
        wget -t inf https://s3.amazonaws.com/Minecraft.Download/versions/$CLIENTVERSION/$CLIENTVERSION.jar
    fi

    
    echo $(date) "Starting server"

    (tail -F -n 0 $CONTROL | /usr/bin/java -jar minecraft_server.$VERSION.jar nogui  & echo $! > /minecraft/minecraft-ctl.sh.pid)



 
;;

stop)
    PID=$(cat /minecraft/minecraft-ctl.sh.pid)
    echo $(date) "Stopping minecraft server"
    echo "/say server restarting in 10 seconds" >> $CONTROL
    sleep 10
    echo "/stop" >> $CONTROL
    

    
    sleep 30
    kill -s 0 $PID && kill -s 9 $PID 
;;



sync)

    echo $(date) "Sending save-all to server"
    echo "/save-off" >> $CONTROL
    sleep 2
    echo "/save-all flush" >> $CONTROL 

    sleep 10

    echo $(date) "Syncing world to backup"

    rsync -av --inplace --delete /minecraft/host/mcdata/world /minecraft/host/otherdata/mcbackup
    #echo "$(date) Creating snapshot"
    # sudo zfs snapshot main/minecraft/world@$(date +%Y%m%d%H%M)

    sleep 10

    echo "/save-on" >> $CONTROL 
    
    
    echo $(date) "sync done"
;;
esac
