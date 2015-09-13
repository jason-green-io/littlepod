#!/bin/bash
cd /minecraft/web
sudo twistd -no web --path=. -p 80 &> >( tee -a /minecraft/minecraft-twistd.log) 
