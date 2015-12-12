#!/bin/bash
DBFILE=/minecraft/host/otherdata/littlepod.db
       (
         flock -n 9 || exit 1
echo "$(date) starting overviewer map update"
UUID=$(uuidgen)
sqlite3 $DBFILE -init <(echo .timeout 20000) "INSERT INTO process (process, id) values (\"map\", \"$UUID\")"
overviewer.py --config=/minecraft/host/config/overviewerconfig.py
sqlite3 $DBFILE -init <(echo .timeout 20000) "UPDATE process SET end = CURRENT_TIMESTAMP WHERE id = \"$UUID\""
echo "$(date) overviewer map update done"
       ) 9>/tmp/overviewer.lock

