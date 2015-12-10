#! /bin/bash

FREE=$(df -B1 | awk '$6 ~ "/minecraft/host" { print $4 }')

echo $FREE


if [[ $FREE -lt 50000000000000 ]]; then
    sed -e '/minecraft-ctl.sh start/ s/^#*/#/' -i /minecraft/minecraft-server.sh
    /minecraft/vanillabean.py "/stop"
    echo "Stopping"
else
    sed -e '/minecraft-ctl.sh start/ s/^#*//' -i /minecraft/minecraft-server.sh
    /minecraft/minecraft-server.sh
    echo "Starting"
fi
