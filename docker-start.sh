#!/bin/bash


if [[ ! -h /minecraft/python-rtmbot/rtmbot.conf ]]; then
    echo "Creating link to rtmbot.conf"
    ln -s /minecraft/host/config/rtmbot.conf /minecraft/python-rtmbot/
    cp /minecraft/rtmbot-plugin* /minecraft/python-rtmbot/plugins
fi

sudo cron

cd /minecraft

if [[ ! -d /minecraft/host/otherdata/logs ]]; then
    echo "Creating folders for other data"
    mkdir -p /minecraft/host/otherdata/logs
else
    echo "Found otherdata and logs folder"
    if [[ ! -f /minecraft/host/otherdata/littlepod.db ]]; then
        echo "Database not found, creating"
        sqlite3 /minecraft/host/otherdata/littlepod.db < /minecraft/create-database.sql
    else
        echo "Found database"
    fi
fi

if [[ ! -d /minecraft/host/webdata ]]; then
    echo "Creating folder for webdata with defaults"
    mkdir -p /minecraft/host/webdata/map
    cp -r /minecraft/skelwebdata/* /minecraft/host/webdata
else
    echo "Found webdata"
fi

if [[ ! -d /minecraft/host/config ]]; then
    echo "Config files not found, creating folder with defaults"
    mkdir /minecraft/host/config
    cp -r /minecraft/skelconfig/* /minecraft/host/config
else
    echo "Found config folder"
fi

if [[ ! -d /minecraft/host/mcdata ]]; then
    echo "Creating folder for Minecraft world data"
    mkdir /minecraft/host/mcdata
    if [[ ! -h /minecraft/host/mcdata/server.properties ]]; then
        echo "Linking config"
        ln -s /minecraft/host/config/server.properties /minecraft/host/mcdata
    else
        echo "Config already linked"
    fi
    if [[ ! -f /minecraft/host/config/eula.txt ]]; then
        echo "Agreeing to eula"
        echo "eula=true" > /minecraft/host/mcdata/eula.txt
    else
        echo "eula already agreed"    
    fi
else
    echo "Found Minecraft world folder"
fi


echo "Customize your config files then run ./minecraft-server.sh"

/bin/bash
