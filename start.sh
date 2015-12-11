#! /bin/bash

sudo cp /minecraft/host/config/cgconfig.conf /etc 

/usr/bin/tmux new -s minecraft -d

/minecraft/minecraft-server.sh

tmux a
