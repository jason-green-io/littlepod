#!/bin/bash
(
         flock -n 9 || exit 1
cd /minecraft
nice -n 2 cgexec -g cpu:overviewer overviewer.py --config=/minecraft/overviewerconfig.py --genpoi
) 9>/tmp/overviewerpoi.lock
