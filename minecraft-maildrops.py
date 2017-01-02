#!/usr/bin/python3
import datetime
import yaml
import sqlite3
import sys
import codecs
from itertools import groupby
sys.path.append("/minecraft")
import showandtellraw
import vanillabean

with open('/minecraft/host/config/server.yaml', 'r') as configfile:    config = yaml.load(configfile)

dbfile = config['dbfile']
servername = config['name']
URL = config['URL']
webdata = config["webdata"]

serverName = "<aqua^\<><green^{}><aqua^\>>".format(servername)
worlddict = { "o" : ["overworld", "0"], "n" : ["nether", "2"], "e" : ["end", "1"] }


def updatePois():
    conn = sqlite3.connect(dbfile)
    cur = conn.cursor()

    cur.execute("SELECT * FROM pois order by type")
    pois = cur.fetchall()

    conn.commit()
    conn.close()

    dimDict = {"o":0, "n": 2, "e": 1}
    

    with codecs.open(webdata + "/pois.md", "w", "utf-8") as file:
        
        file.write("""# POIs\n""")

        
        for poiType, poiList in groupby(pois, lambda x: x[1].strip("*")):
            print(repr(poiType.strip().strip("*")))
            file.write("""## {}
|name|
|:-|
""".format(poiType.strip("*")))

            for poi in poiList:
                coords = poi[0].split(",")
                dim = dimDict[coords.pop(0)]
                link = "http://{}/map/#/{}/{}/{}/-2/{}/0".format(URL, coords[0], coords[1], coords[2], dim)
                webline = u"|[{}]({})|\n".format(" ".join([ poi[2], poi[3], poi[4]]), link)
                file.write(webline)
            






    

                                    





def sendMaildrops():
    conn = sqlite3.connect(dbfile)
    cur = conn.cursor()

    cur.execute("SELECT * FROM maildrop natural join onlineplayers WHERE inverted = 0 and slots > 0 COLLATE NOCASE")
    maildrop = cur.fetchall()

    cur.execute("SELECT * FROM maildrop natural join onlineplayers WHERE inverted = 1 and slots = 0 COLLATE NOCASE")
    maildropinv = cur.fetchall()

    for mail in maildrop + maildropinv:
        dimcoords, boxname, desc, slots, hidden, inverted = mail
        dim, coords = dimcoords.split(",",1)

        if dim == "e":
            worldnum = "1"
        elif dim == "n":
            worldnum = "2"
        elif dim == "o":
            worldnum = "0"
        
        URLcoords = coords.replace(",", "/")           

        toserver = '/tellraw ' + boxname + ' ' + showandtellraw.tojson(serverName + ' {{Maildrop [_{}_|http://{}/map/#/{}/-1/{}/0]~{} {}}} {}'.format(desc if desc else "{} {}".format(worlddict[dim][0], coords), URL, URLcoords, worldnum, worlddict[dim][0], coords, "has {} items".format(slots) if slots else "is empty") )
        vanillabean.send( toserver )
        print(toserver)

    

    conn.commit()
    conn.close()


sendMaildrops()
updatePois()
