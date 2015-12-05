#!/bin/bash
#rsync -a /minecraft/worlddisk/ /run/shm/world

cgexec -g blkio,cpu:minecraft java -jar $(ls /minecraft/minecraft_server.15w* | tail -n 1) nogui

