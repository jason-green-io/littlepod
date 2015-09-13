#!/bin/bash

       (
         flock -n 9 || exit 1
echo "$(date) starting overviewer map update"
nice -n 2 cgexec -g cpu:overviewer overviewer.py --config=/minecraft/overviewerconfig.py

echo "$(date) overviewer map update done"
       ) 9>/tmp/overviewer.lock

