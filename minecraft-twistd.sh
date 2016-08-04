#!/bin/bash
cd /minecraft/host/webdata
rm twistd.pid
sudo twistd -no web --path=. -p 80 
