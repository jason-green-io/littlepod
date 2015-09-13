#!/bin/bash
#rsync -a /minecraft/worlddisk/ /run/shm/world

sudo nice -n -2 cgexec -g cpu:minecraft java -XX:+UseG1GC -Xms2048M -Xmx2048M -jar /minecraft/minecraft_server.15w37a.jar nogui

