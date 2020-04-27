#!/bin/bash
# vim: ts=4 sw=4 sts=4 et :

(

    /usr/bin/flock -n 9 || exit 1
    trap "kill 0" EXIT

    function commands () {
        echo "$(printenv | grep MC_ | cut -d "_" -f2-)" | while read -r PROP; do
            if [ ! -z "$PROP" ]; then
                TARGET_KEY=$(echo $PROP | cut -d '=' -f1 | tr '_' '-')
                REPLACEMENT_VALUE=$(echo $PROP | cut -d '=' -f2)
                echo "s/\($TARGET_KEY *= *\).*/\1$REPLACEMENT_VALUE/"
            fi
        done
    }
    case $TYPE in
        bds)
            if [[ ! -d $DATAFOLDER/bds ]]; then
                echo $(date) "Creating folder for Minecraft world data"
                mkdir $DATAFOLDER/bds

            else
                echo $(date) "Found Minecraft world folder"
            fi

            if [[ ! -d /tmp/server_$MCVERSION ]]; then
                echo $(date) "Downloading server version $MCVERSION"
                curl -o /tmp/server_$MCVERSION.zip https://minecraft.azureedge.net/bin-linux/bedrock-server-$MCVERSION.zip
                mkdir /tmp/server_$MCVERSION
                /usr/bin/unzip /tmp/server_$MCVERSION.zip -d /tmp/server_$MCVERSION

            fi
            cd /tmp/server_$MCVERSION

            for each in $DATAFOLDER/bds/*; do
                [ -e "$each" ] || continue
                echo $each
                rm -r $(basename $each)
                ln -s $each $(basename $each)
            done

            echo $(date) "Starting server version $MCVERSION"

            sed -i.bak -f <(commands) /tmp/server_$MCVERSION/server.properties
            coproc ncat -lkp 7777 -o $DATAFOLDER/logs/bds.log
            export LD_LIBRARY_PATH=/tmp/server_$MCVERSION
            ./bedrock_server <&${COPROC[0]} >&${COPROC[1]} 2>&1
            echo $(date) "Server has stopped"

        ;;

    
        mc)

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
            
            
            sed -f <(commands) /littlepod/server.properties > server.properties



            if [[ ! -f "/tmp/server_$MCVERSION.jar" ]]; then
                echo $(date) "Downloading server version $MCVERSION"
                curl -o "/tmp/server_$MCVERSION.jar" $(curl $(curl https://launchermeta.mojang.com/mc/game/version_manifest.json | jq --arg ver "$MCVERSION" -r '.versions[] | select(.id == $ver).url') | jq -r '.downloads.server.url')
            fi

            echo $(date) "Starting server version $MCVERSION"

            coproc ncat -lkp 7777
            /usr/bin/java -javaagent:/littlepod/jolokia-jvm-1.6.2-agent.jar -Xmx8G -XX:+UnlockExperimentalVMOptions -XX:+UseG1GC -XX:G1NewSizePercent=20 -XX:G1ReservePercent=20 -XX:MaxGCPauseMillis=50 -XX:G1HeapRegionSize=32M -jar "/tmp/server_$MCVERSION.jar" nogui <&${COPROC[0]} >&${COPROC[1]} 2>&1
            echo $(date) "Server has stopped"

        ;;
    esac
) 9> /tmp/minecraft_server >> $DATAFOLDER/logs/commandblock.log &
