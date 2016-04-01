#!/usr/bin/python

import datetime
import time
import json
import glob
import sys
import os
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



def genpoimarkers( start, end, dim ):
    print(start, end, dim)
    dimdict = { "o" : "0", "n": "-1", "e": "1"}
    conn = sqlite3.connect(dbfile, timeout=20)
    cur = conn.cursor()

    cur.execute('SELECT datetime, name, x, y, z FROM location NATURAL JOIN playerUUID WHERE datetime > datetime("now", "' + start + '") AND datetime < datetime("now", "' + end + '") AND dim == ' + dimdict[dim])
    data = cur.fetchall()

    conn.commit()
    conn.close()
    players = {poi[1] for poi in data}
    keys = ("datetime","name","x","y","z")

    return ([dict(zip(keys, poi), id="player") for poi in data], [dict(checked=True, name="player " + player, icon="https://minotar.net/avatar/"+player+"/16", filterFunction=genfilter(player)) for player in players])
