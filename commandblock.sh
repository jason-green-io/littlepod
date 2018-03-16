#!/bin/bash
(

    /usr/bin/flock -n 9 || exit 1
    trap "kill 0" EXIT
    if [[ ! -d /minecraft/host/mcdata ]]; then
        echo $(date) "Creating folder for Minecraft world data"
        mkdir /minecraft/host/mcdata

    else
        echo $(date) "Found Minecraft world folder"
    fi

    cd /minecraft/host/mcdata

    echo $(date) "Agreeing to EULA"
    echo "eula=true" > /minecraft/host/mcdata/eula.txt

    echo $(date) "Creating server.properties"
    envsubst < /minecraft/server.properties.envsubst > /minecraft/host/mcdata/server.properties



    MCVERSION=$(cat /minecraft/mcversion)


    if [[ ! -f /minecraft/host/mcdata/minecraft_server.$MCVERSION.jar ]]; then
        echo $(date) "Downloading version $MCVERSION"
        /usr/bin/wget -t inf https://s3.amazonaws.com/Minecraft.Download/versions/$MCVERSION/minecraft_server.$MCVERSION.jar 2>&1

    fi

    echo $(date) "Starting server version $MCVERSION"

    coproc ncat -lkp 7777
    /usr/bin/java -jar /minecraft/host/mcdata/minecraft_server.$MCVERSION.jar nogui <&${COPROC[0]} >&${COPROC[1]} 2>&1
    echo $(date) "Server has stopped"


) 9> /tmp/minecraft_server >> $OTHERDATA/logs/commandblock.log &
