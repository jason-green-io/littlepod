#!/bin/bash
cd /minecraft/host/webdata
sudo twistd -no web --path=. -p 80 &> >( tee -a /minecraft/host/otherdata/logs/minecraft-twistd.log) 
