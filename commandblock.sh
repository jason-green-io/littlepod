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



    MCVERSION=$1


    if [[ ! -f /minecraft/host/mcdata/server_$MCVERSION.jar ]]; then
        echo $(date) "Downloading server version $MCVERSION"
        curl -o server_$MCVERSION.jar $(curl $(curl https://launchermeta.mojang.com/mc/game/version_manifest.json | jq --arg ver $MCVERSION -r '.versions[] | select(.id == $ver).url') | jq -r '.downloads.server.url')
    fi

    echo $(date) "Starting server version $MCVERSION"

    coproc ncat -lkp 7777
    /usr/bin/java -jar /minecraft/host/mcdata/server_$MCVERSION.jar nogui <&${COPROC[0]} >&${COPROC[1]} 2>&1
    echo $(date) "Server has stopped"


) 9> /tmp/minecraft_server >> $OTHERDATA/logs/commandblock.log &
