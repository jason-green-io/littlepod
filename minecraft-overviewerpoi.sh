#!/bin/bash
DBFILE=/minecraft/host/otherdata/littlepod.db
(
         flock -n 9 || exit 1
cd /minecraft

/minecraft/minecraft-ctl.sh sync

UUID=$(uuidgen)
sqlite3 $DBFILE -init <(echo .timeout 20000) "INSERT INTO process (process, id) values (\"poi\", \"$UUID\")"
sqlite3 $DBFILE -init <(echo .timeout 20000) "CREATE TABLE tempmaildrop (coords primary key, name, desc, slots, hidden, inverted)"
sqlite3 $DBFILE -init <(echo .timeout 20000) "DROP TABLE pois"
sqlite3 $DBFILE -init <(echo .timeout 20000) "CREATE TABLE pois (coords primary key, type, text1, text2, text3)"

python /usr/lib/python2.7/dist-packages/overviewer_core/aux_files/genPOI.py --config=/minecraft/host/config/overviewerconfig.py

sqlite3 $DBFILE -init <(echo .timeout 20000) "DROP TABLE maildrop; ALTER TABLE tempmaildrop RENAME TO maildrop"
sqlite3 $DBFILE -init <(echo .timeout 20000) "UPDATE process SET end = CURRENT_TIMESTAMP WHERE id = \"$UUID\""

/minecraft/minecraft-maildrops.py


/minecraft/minecraft-chestactivity.py

/minecraft/minecraft-overviewerpoiadmin.sh

) 9>/tmp/overviewerpoi.lock
