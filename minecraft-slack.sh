#!/bin/bash
cd /minecraft/python-rtmbot
python -u /minecraft/python-rtmbot/rtmbot.py &> >(tee -a /minecraft/host/otherdata/logs/minecraft-slack.log) 

