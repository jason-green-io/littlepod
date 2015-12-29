#!/usr/bin/python

import datetime
import time
import json
import glob
import sys
import os
import nbt2yaml
import yaml
import sqlite3

with open('/minecraft/host/config/server.yaml', 'r') as configfile:
    config = yaml.load(configfile)

dbfile = config['dbfile']

def genfilter(name):
    def filter(poi):
        if poi['id'] == 'player' and poi["name"] == name:
            return poi['name'] + '\n' + poi["datetime"] + "\n" + str(poi['x']) +" "+str(poi['y']) + " " + str(poi['z'])
    return filter


timeframe = '"-7 days"'

conn = sqlite3.connect(dbfile, timeout=20)
cur = conn.cursor()

cur.execute('SELECT datetime, name, x, y, z FROM location NATURAL JOIN playerUUID WHERE datetime > datetime("now", '+timeframe+') AND dim == 0')
over = cur.fetchall()
cur.execute('SELECT datetime, name, x, y, z FROM location NATURAL JOIN playerUUID WHERE datetime > datetime("now", '+timeframe+') AND dim == -1')
nether = cur.fetchall()
cur.execute('SELECT datetime, name, x, y, z FROM location NATURAL JOIN playerUUID WHERE datetime > datetime("now", '+timeframe+') AND dim == 1')
end = cur.fetchall()

conn.commit()
conn.close()
players = {poi[1] for poi in over + nether + end}
print players
keys = ("datetime","name","x","y","z")

overpoi = [dict(zip(keys, poi), id="player") for poi in over]
netherpoi = [dict(zip(keys, poi), id="player") for poi in nether]
endpoi = [dict(zip(keys, poi), id="player") for poi in end]

markers =[dict(name="player " + player, icon="https://minotar.net/avatar/"+player+"/16", filterFunction=genfilter(player)) for player in players]
print markers
