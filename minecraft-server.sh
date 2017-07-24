#!/bin/bash
cd /minecraft

echo "Starting processes"
sudo monit -c /minecraft/host/config/monitrc


