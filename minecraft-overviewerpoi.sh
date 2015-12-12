#!/bin/bash
DBFILE=/minecraft/host/otherdata/littlepod.db
(
         flock -n 9 || exit 1
cd /minecraft
UUID=$(uuidgen)
sqlite3 $DBFILE -init <(echo .timeout 20000) "INSERT INTO process (process, id) values (\"poi\", \"$UUID\")"
overviewer.py --config=/minecraft/host/config/overviewerconfig.py --genpoi
sqlite3 $DBFILE -init <(echo .timeout 20000) "UPDATE process SET end = CURRENT_TIMESTAMP WHERE id = \"$UUID\""
) 9>/tmp/overviewerpoi.lock
