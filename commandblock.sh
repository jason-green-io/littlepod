#!/bin/bash
(

    /usr/bin/flock -n 9 || exit 1
    trap "kill 0" EXIT
    if [[ ! -d $DATAFOLDER/mc ]]; then
        echo $(date) "Creating folder for Minecraft world data"
        mkdir $DATAFOLDER/mc

    else
        echo $(date) "Found Minecraft world folder"
    fi

    cd $DATAFOLDER/mc

    echo $(date) "Agreeing to EULA"
    echo "eula=true" > eula.txt

    echo $(date) "Creating server.properties"
    
    function commands () {
    echo "$(printenv | grep MC_ | cut -d "_" -f2-)" | while read -r PROP; do
        if [ ! -z "$PROP" ]; then
            TARGET_KEY=$(echo $PROP | cut -d '=' -f1 | tr '_' '-')
            REPLACEMENT_VALUE=$(echo $PROP | cut -d '=' -f2)
            echo "s/\($TARGET_KEY *= *\).*/\1$REPLACEMENT_VALUE/"
        fi
    done
    }
    
    sed -f <(commands) /minecraft/server.properties > server.properties

    MCVERSION=$1


    if [[ ! -f /tmp/server_$MCVERSION.jar ]]; then
        echo $(date) "Downloading server version $MCVERSION"
        curl -o /tmp/server_$MCVERSION.jar $(curl $(curl https://launchermeta.mojang.com/mc/game/version_manifest.json | jq --arg ver $MCVERSION -r '.versions[] | select(.id == $ver).url') | jq -r '.downloads.server.url')
    fi

    echo $(date) "Starting server version $MCVERSION"

    coproc ncat -lkp 7777
    /usr/bin/java -jar /tmp/server_$MCVERSION.jar nogui <&${COPROC[0]} >&${COPROC[1]} 2>&1
    echo $(date) "Server has stopped"


) 9> /tmp/minecraft_server >> $DATAFOLDER/logs/commandblock.log &
