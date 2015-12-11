#!/bin/bash

mv /minecraft/rtmbot-plugin* /minecraft/python-rtmbot/plugins

cp /minecraft/host/config/rtmbot.conf /minecraft/python-rtmbot

/minecraft/minecraft-server.sh

/bin/bash
