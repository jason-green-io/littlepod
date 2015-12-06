#!/bin/bash
#rsync -a /minecraft/worlddisk/ /run/shm/world

VERSION=$(cat /minecraft/host/config/mcversion)

cd /minecraft/host/mcdata

if [[ ! -f minecraft_server.$VERSION.jar ]]; then

	wget -t inf https://s3.amazonaws.com/Minecraft.Download/versions/$VERSION/minecraft_server.$VERSION.jar
fi

java -jar minecraft_server.$VERSION.jar nogui

