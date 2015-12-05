#!/bin/bash
(
         flock -n 9 || exit 1
cd /minecraft
UUID=$(uuidgen)
sqlite3 /minecraft/barlynaland.db -init <(echo .timeout 20000) "INSERT INTO process (process, id) values (\"poi\", \"$UUID\")"
cgexec -g blkio,cpu:overviewer /minecraft/Minecraft-Overviewer-master/overviewer.py --config=/minecraft/overviewerconfig.py --genpoi
sqlite3 /minecraft/barlynaland.db -init <(echo .timeout 20000) "UPDATE process SET end = CURRENT_TIMESTAMP WHERE id = \"$UUID\""
) 9>/tmp/overviewerpoi.lock
