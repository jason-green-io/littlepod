#!/bin/bash
X=$1
Z=$2
RADIUS=$3

QUERY="select * from location natural join playerUUID where x > $(($X - $RADIUS)) and x < $(($X + $RADIUS)) and z > $(($Z - $RADIUS)) and z < $(($Z + $RADIUS)) and datetime > datetime('now', '-1 month')"
echo "$QUERY"

QUERY2="select datetime, name, dim, x ,y, z, stats from stats join location using (datetime, UUID) natural join playerUUID where x > $(($X - $RADIUS)) and x < $(($X + $RADIUS)) and z > $(($Z - $RADIUS)) and z < $(($Z + $RADIUS))"
sqlite3 /minecraft/host/otherdata/littlepod.db "$QUERY"
