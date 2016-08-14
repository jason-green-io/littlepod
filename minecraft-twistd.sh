#!/bin/bash
cd /minecraft/host/webdata
rm -f twistd.pid 2> /dev/null
sudo twistd -no web --path=. -p 80 
