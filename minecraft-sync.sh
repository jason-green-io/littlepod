#!/bin/bash


echo "$(date) Sending sava-all to server"
/minecraft/vanillabean.py "/save-all" 


sleep 10

#echo "$(date) Syncing ramdisk with disk"
#rsync -av /run/shm/world/ /minecraft/worlddisk 

echo "$(date) Creating snapshot"
sudo zfs snapshot main/minecraft/world@$(date +%Y%m%d%H%M)

sleep 10

#echo "$(date) Running overviewer to update POI"
#/minecraft/minecraft-overviewerpoi.sh &>> /minecraft/minecraft-overviewerpoi.log &

echo "$(date) sync done"
