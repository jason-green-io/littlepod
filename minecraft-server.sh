#!/bin/bash
cd /minecraft
echo "Creating tmux session"
tmux new -s minecraft -d

echo "Starting processes"
pm2 start /minecraft/littlepod.json

echo "Starting minecraft server"
/minecraft/minecraft-ctl.sh start



#echo "Starting web sever"
#tmux neww -t minecraft:6 '/minecraft/minecraft-twistd.sh'

#echo "Starting murmur"
#tmux neww -t minecraft:5 '/minecraft/minecraft-murmur.sh'

#echo "Starting notify"
#tmux neww -t minecraft:8 '/minecraft/minecraft-notify.sh'

#echo "Starting player activity"
#tmux neww -t minecraft:9 '/minecraft/minecraft-playeractivity.py'

#echo "Starting slack integration"
#tmux neww -t minecraft:4 '/minecraft/minecraft-slack.sh'
#echo "Starting discord integration"
#tmux neww -t minecraft:5 '/minecraft/minecraft-discord.sh'
