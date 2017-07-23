#!/bin/bash
DBFILE=/minecraft/host/otherdata/littlepod.db
(
         flock -n 9 || exit 1
cd /minecraft

/minecraft/minecraft-ctl.sh sync

UUID=$(uuidgen)

sqlite3 $DBFILE -init <(echo .timeout 20000) "INSERT INTO process (process, id) values (\"poi\", \"$UUID\")"

overviewer.py --config=/minecraft/host/config/overviewerconfig.py --genpoi "general"

sqlite3 $DBFILE -init <(echo .timeout 20000) "UPDATE process SET end = CURRENT_TIMESTAMP WHERE id = \"$UUID\""

/minecraft/minecraft-maildrops.py

#/minecraft/minecraft-chestactivity.py

#/minecraft/minecraft-overviewerpoiadmin.sh

) 9>/tmp/overviewerpoi.lock
