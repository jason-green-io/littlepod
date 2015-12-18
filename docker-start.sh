#!/bin/bash


if [[ ! -h /minecraft/python-rtmbot/rtmbot.conf ]]; then
    echo "Creating link to rtmbot.conf"
    ln -s /minecraft/host/config/rtmbot.conf /minecraft/python-rtmbot/
    mv /minecraft/rtmbot-plugin* /minecraft/python-rtmbot/plugins
fi

sudo cron

cd /minecraft

if [[ ! -d /minecraft/host/otherdata/logs ]]; then
   echo "Creating folders for other data"
    mkdir -p /minecraft/host/otherdata/logs
else
   echo "Found otherdata and logs"
fi

if [[ ! -d /minecraft/host/webdata ]]; then
    echo "Creating folder for webdata"
    mkdir -p /minecraft/host/webdata/map
else
    echo "Found webdata"
fi

if [[ ! -d /minecraft/host/mcdata ]]; then
    echo "Creating folder for Minecraft world data"
    mkdir /minecraft/host/mcdata
else
    echo "Found Minecraft world folder"
fi

if [[ ! -d /minecraft/host/config ]]; then
    echo "Config files not found, creating folder with defaults"
    mv skelconfig /minecraft/host/config
else
    echo "Found config folder"
fi

echo "Customize your config files then run ./minecraft-server.sh"

/bin/bash
