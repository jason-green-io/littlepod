#!/bin/bash
cd /minecraft

echo "Starting processes"
chmod 700 /minecraft/host/config/monitrc
sudo monit -c /minecraft/host/config/monitrc


