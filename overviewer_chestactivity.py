#!/usr/bin/python

import json
import yaml
import time
import os
import glob
import sqlite3

from collections import defaultdict


with open('/minecraft/host/config/server.yaml', 'r') as configfile:
    config = yaml.load(configfile)

dbfile = config['dbfile']
otherdata =config["otherdata"]


def chestsOverworld(poi):
    return chestsUniversal(poi, "o")


def chestsNether(poi):
    return chestsUniversal(poi, "n")


def chestsEnd(poi):
    return chestsUniversal(poi, "e")

def chestsUniversal( poi, dim ):
    if poi['id'] in ['Chest', "minecraft:chest"]:
        
        #filetime = time.strftime("%Y%m%d%H%M")
        chestfile = otherdata + '/chests/latest' + "." + dim + '.json'
        if not os.path.exists(os.path.dirname(chestfile)):
            os.makedirs(os.path.dirname(chestfile))
        with open( chestfile, 'a+' ) as file:

            file.write( json.dumps(poi) + '\n' )



def filterchest0(poi):
    if poi['id'] == 'chestactivity':
        return poi['name']


chest0 = [ dict(name="Chest Activity - today", icon="icons/black/chest.png", filterFunction=filterchest0, createInfoWindow=True, checked=True)]



def genpoi( start, end, dim ):
    print(start, end, dim)
    dimdict = { "o" : "0", "n": "-1", "e": "1"}
    conn = sqlite3.connect(dbfile, timeout=20)
    cur = conn.cursor()

    cur.execute('SELECT coords, group_concat(ts || "," || chest, "|") FROM chests WHERE ts > datetime("now", "{}") AND ts < datetime("now", "{}") AND substr(coords, 1,1) == "{}" group by coords'.format(start, end, dim))
    data = cur.fetchall()
    # print(data)
    conn.commit()
    conn.close()

    keys = ("name","x","y","z")
    pois = []
    chestlist = []
    for chest in data:
        # print(chest)
        (dim, x, y, z) = tuple(chest[0].split(","))
        name = ""
        for timeitem in chest[1].split("|"):
            (timestamp, items) = tuple(timeitem.split(",", 1))
            name += timestamp + "</br>"
            # print(items)
            for item in json.loads(items).items():
                # print(item)
                name += str(item) + "</br>"
            
        pois.append((name, x, y, z))
    return [dict(zip(keys, poi), id="chestactivity") for poi in pois]




markers = chest0

overmarker = [ dict(name="Chest Activity generator over", filterFunction=chestsOverworld, checked=False) ]
nethermarker = [ dict(name="Chest Activity generator nether", filterFunction=chestsNether, checked=False) ]
endmarker = [ dict(name="Chest Activity generator end", filterFunction=chestsEnd, checked=False) ]



