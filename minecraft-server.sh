#!/bin/bash
cd /minecraft
echo "Creating tmux session"
tmux new -s minecraft -d

echo "Starting processes"
pm2 start /minecraft/host/config/littlepod.pm2.json


