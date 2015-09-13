#!/bin/bash
/minecraft/vanillabean.py "/say server restarting in 30 seconds"
sleep 30
/minecraft/minecraft-sync.sh &>> /minecraft/minecraft-sync.log

/minecraft/vanillabean.py "/stop"
sleep 10
/minecraft/minecraft-server.sh
