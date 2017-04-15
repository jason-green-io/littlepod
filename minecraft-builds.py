#!/usr/bin/python3 -u
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

def getStat(stats, stat):
    return eval(stats).get(stat,0)


conn.create_function("getStat", 2, getStat)

cur.execute('select name, UUID, datetime as "ts [timestamp]", status, twitter, twitch, youtube, reddit from (select *, count(getStat(stats, "stat.playOneMinute")) as count from stats natural join playerUUID WHERE (datetime > datetime("now", "-14 day") AND name != "") group by name order by datetime ) natural left join status order by count desc')
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
    dateNow = time.strftime("%Y-%m-%d")
    thumbsFolder = "/minecraft/host/webdata/thumbs/"
    for each in builds:
        name = each[0]
        if name.lower() in players:
            coords = each[1].split("|")
            buildfinal.append( "## {}".format(name.replace("_", "\_")))
            for coord in coords:
                link = coordstolink(coord)

                buildFolder = name + "/" + coord + "/"
                
                buildPngName = timeNow + ".png"
                buildPng = thumbsFolder + buildFolder + buildPngName

                buildGifName = coord + ".gif"
                buildGif = thumbsFolder + buildFolder + buildGifName
                
                os.makedirs(thumbsFolder + name, exist_ok=True)
                phantomjsLink = coordstolink(coord).replace(URL,"127.0.0.1")
                command = ["/usr/bin/phantomjs", "--debug=true", "--ssl-protocol=tlsv1", "/minecraft/minecraft-builds.js", phantomjsLink, thumbsFolder + buildFolder + "temp.png"]
                subprocess.call(command, shell=False, timeout=10)
                command = "/usr/bin/convert {0}temp.png -gravity southeast -stroke '#000C' -strokewidth 2 -annotate 0 {1} -stroke none -fill white -annotate 0 {1} {2}; rm {0}temp.png".format(thumbsFolder + buildFolder, dateNow, buildPng)
                subprocess.call(command, shell=True)
                command = "convert -delay 10 {}*.png {}".format(thumbsFolder + buildFolder, buildGif)
                subprocess.call(command, shell=True)
                buildfinal.append( "[![{}](thumbs/{})]({})\n[gif]({})\n".format(coord, buildFolder + buildPngName, link, "thumbs/" + buildFolder + buildGifName))
    return "\n".join(buildfinal)




buildfinal = genbuilds(builds, players + oldplayers)
with open(webdata + "/builds.md", "w") as outfile:
    outfile.write(buildfinal)

