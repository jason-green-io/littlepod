#!/bin/bash
cd /minecraft/python-rtmbot
/minecraft/python-rtmbot/rtmbot.py &> >(tee -a /minecraft/host/otherdata/logs/minecraft-slack.log) 

