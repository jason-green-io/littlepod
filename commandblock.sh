#!/bin/bash
{
    
    flock -n 9 || exit 1
    trap "kill 0" EXIT
    if [[ ! -d /minecraft/host/mcdata ]]; then
	echo $(date) "Creating folder for Minecraft world data"
	mkdir /minecraft/host/mcdata
	
	if [[ ! -f /minecraft/host/mcdata/server.properties ]]; then
	    echo $(date) "Creating server.properties"
	    envsubst < /minecraft/server.properties.envsubst > /minecraft/host/mcdata/server.properties
	else
	    echo $(date) "Found server.properties"
	fi

	if [[ ! -f /minecraft/host/mcdata/eula.txt ]]; then
	    echo $(date) "Agreeing to EULA"
	    echo "eula=true" > /minecraft/host/mcdata/eula.txt
	else
	    echo $(date) "EULA already agreed"
	fi
    else
	echo $(date) "Found Minecraft world folder"
    fi



    MCVERSION=$(cat /minecraft/mcversion)

    cd /minecraft/host/mcdata

    if [[ ! -f minecraft_server.$MCVERSION.jar ]]; then
	echo $(date) "Downloading version $MCVERSION"
	wget -t inf https://s3.amazonaws.com/Minecraft.Download/versions/$MCVERSION/minecraft_server.$MCVERSION.jar 2>&1
    
    fi
    
    echo $(date) "Starting server version $MCVERSION"

    coproc ncat -lkp 7777
    /usr/bin/java -jar minecraft_server.$MCVERSION.jar nogui <&${COPROC[0]} >&${COPROC[1]} 2>&1
    echo $(date) "Server has stopped"
	

} 9> /tmp/minecraft_server &





