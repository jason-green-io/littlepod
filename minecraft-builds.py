import os
import yaml
import time
import datetime

import sqlite3
import subprocess

with open('/minecraft/host/config/server.yaml', 'r') as configfile:
    config = yaml.load(configfile)


dbfile = config['dbfile']
mcfolder = config['mcdata']
URL = config['URL']
servername = config['name']
webdata = config['webdata']
otherdata = config["otherdata"]

config = '/minecraft/host/config'




conn = sqlite3.connect(dbfile, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
cur = conn.cursor()

cur.execute('select name, group_concat(coords,"|") from maildrop where hidden != 1 group by name')
builds = cur.fetchall()


cur.execute("SELECT * FROM groups")
players = cur.fetchall()


cur.execute('select name, UUID, date as "ts [timestamp]", status, twitter, twitch, youtube, reddit from (select * from (select * from joins order by date asc) group by UUID) natural join whitelist natural join playerUUID natural left join status where date <= datetime("now", "-14 days") group by name order by date desc')
oldplayers = cur.fetchall()

def coordstolink(coords):
    worlddict = { "o" : ["overworld", "0"], "n" : ["nether", "2"], "e" : ["end", "1"] }    
    dim, x, y, z = tuple(coords.split(","))
    return "http://" + URL + "/map/#/" + x + "/" + y + "/" + z + "/-2/" + worlddict[dim][1] + "/0"


def genbuilds(builds, players):
    buildfinal =[] 
    players =  [player[0].lower() for player in players]
    timeNow = str(int(time.time()))
    thumbsFolder = "/minecraft/host/webdata/thumbs"
    for each in builds:
        name = each[0]
        if name.lower() in players:
            coords = each[1].split("|")
            buildfinal.append( "## {}".format(name.replace("_", "\_")))
            for coord in coords:
                link = coordstolink(coord)
                buildFolder = name + "/" + coord
                buildPngName = timeNow + ".png"
                buildPng = thumbsFolder + "/" + buildFolder + "/" + buildPngName
                os.makedirs(thumbsFolder + name, exist_ok=True)
                phantomjsLink = coordstolink(coord).replace(URL,"127.0.0.1")
                command = ["/usr/bin/phantomjs", "--debug=true", "--ssl-protocol=tlsv1", "/minecraft/minecraft-builds.js", phantomjsLink, buildPng]
                subprocess.call(command, shell=False, timeout=10)
                buildfinal.append( "[!["+ coord + "](thumbs/" + buildFolder + "/" + buildPngName +  ")](" + link + ")")
    return "\n".join(buildfinal)




buildfinal = genbuilds(builds, players + oldplayers)
with open(webdata + "/builds.md", "w") as outfile:
    outfile.write(buildfinal)

