#!/usr/bin/python3

import os
import yaml
import time
import datetime
import showandtellraw
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

servergradient = ["#FFAA00", "#F69900", "#EE8800", "#E57600", "#DD6600", "#D45500", "#CC4400", "#C33300", "#BB2100", "#B21000", "#AA0000", "#970000", "#840000", "#710000", "#5E0000", "#4B0000", "#380000", "#250000", "#120000", "#000000"]
oldgradient = ["#FFAA00", "#F08D00", "#E27100", "#D45500", "#C63800", "#B81C00", "#AA0000", "#880000", "#660000", "#440000", "#210000", "#000000"]
gradient = ["#FFAA00", "#FCA400", "#F99E00", "#F69900", "#F39300", "#F08D00", "#EE8800", "#EB8200", "#E87C00", "#E57600", "#E27100", "#DF6B00", "#DD6600", "#DA6000", "#D75A00", "#D45500", "#D14F00", "#CE4900", "#CC4400", "#C93E00", "#C63800", "#C33300", "#C02D00", "#BD2700", "#BB2100", "#B81C00", "#B51600", "#B21000", "#AF0B00", "#AC0500", "#AA0000", "#A40000", "#9E0000", "#980000", "#920000", "#8C0000", "#860000", "#800000", "#7B0000", "#750000", "#6F0000", "#690000", "#630000", "#5D0000", "#570000", "#520000", "#4C0000", "#460000", "#400000", "#3A0000", "#340000", "#2E0000", "#290000", "#230000", "#1D0000", "#170000", "#110000", "#0B0000", "#050000", "#000000"]


def gengroups(players):
    groupsfinal = ""
    fontstyle = ""
    for player in players:
        # print player
        playername, UUID, lastlogin, status, twitter, twitch, youtube, reddit = player

        timediff = datetime.datetime.now() - lastlogin
        s = timediff.seconds
        hours, remainder = divmod(s, 3600)
        minutes, seconds = divmod(remainder, 60)
        if timediff.days >= 14:
            last = '%s days' % (timediff.days)
            
        elif timediff.days == 1:
        
            last = '%s day %02d:%02d' % (timediff.days, hours, minutes)
        elif timediff.days > 0:
        
            last = '%s days %02d:%02d' % (timediff.days, hours, minutes)
        else:
            last = '%02d:%02d' % (hours, minutes)

        social = ""

        if youtube:
            social += '[![youtube](youtube.png)](http://youtube.com/' + youtube + ')'
        if twitter:
            social += '[![twitter](twitter.png)](http://twitter.com/' + twitter + ')'
        if reddit:
            social += '[![reddit](reddit.png)](http://reddit.com/u/' + reddit + ')'
        if twitch:
            social += '[![twitch](twitch.png)](http://twitch.tv/' + twitch + ')'

        if social:
            social += '</br>'
        playerstatus = maildropstatus = statusstatus = ''
        if status:
            playerstatus =  str(status) + "</br>"
        else:
            playerstatus = ""

        groupsfinal += "|![](https://minotar.net/avatar/" + playername + "/32)`"  + playername  + '`</br>' + social + playerstatus + last + "|\n"


    return groupsfinal


def genshame(shame):
    shamefinal =""
    print(shame)
    for each in shame:
        lastlogin, playername, UUID, ip, ts = each
        shamefinal += "|" + playername + "|" + str(lastlogin) + "|\n"

    return shamefinal


def getStat(stats, stat):
    return eval(stats).get(stat,0)
             

conn = sqlite3.connect(dbfile, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
cur = conn.cursor()
conn.create_function("getStat", 2, getStat)





cur.execute('select name, UUID, datetime as "ts [timestamp]", status, twitter, twitch, youtube, reddit from (select *, count(getStat(stats, "stat.playOneMinute")) as count from stats natural join playerUUID WHERE (datetime > datetime("now", "-14 day") AND name != "") group by name order by datetime ) natural left join status order by count desc')

players = cur.fetchall()


cur.execute('select name, UUID, date as "ts [timestamp]", status, twitter, twitch, youtube, reddit from (select * from (select * from joins order by date asc) group by UUID) natural join whitelist natural join playerUUID natural left join status where date <= datetime("now", "-14 days") group by name order by date desc')
oldplayers = cur.fetchall()

cur.execute("SELECT * FROM shame")
shame = cur.fetchall()

cur.execute('select name, sum(getStat(stats, "stat.playOneMinute")) / 20 / 60 as total from playeractivity natural join playerUUID where datetime > datetime("now", "-7 days") group by name order by total  desc')
quickie = cur.fetchall()

cur.execute('select count(name) from whitelist')
numwhitelist = cur.fetchall()[0][0]

conn.close

space =20 * "="
space2 = 7 * "="

statsplayers = """# Status

## List of fame

list of players that have been online in the last 2 weeks sorted by playtime

shows: player head, name, social media links, status message and last seen

|player|
|---|
"""

statsoldplayers = """## List of shame

list of players that haven't been online for greater than 2 weeks

|player|
|---|
"""




statsshame = """## List of shame

list of players that haven't played on the server in over 2 weeks! Shaaaaaame!

|name|last seen|
|-|-:|
"""

stats = statsplayers + gengroups(players) + statsoldplayers + gengroups(oldplayers)

totalminutes = 0
for each in quickie:
    totalminutes += each[1]

totalplayer = len(quickie)


with open(otherdata + "/quickie.txt", "w") as outfile:
    line = ("<gold^last 7 d: ><dark_purple^" +
            str(totalplayer) +
            "><gold^\\\\>" +
            "<dark_purple^" + str(numwhitelist) + " >" +
            "<gold^players seen, ><dark_purple^" +
            "%.1F" % (totalminutes / 60.0) +
            "><gold^ h, average ><dark_purple^" +
            "%.1F" % (totalminutes / 60.0 / totalplayer) +
            "><gold^ h\/player>")
    print(line)
    outfile.write(line)

filenames = [config + '/topmotd.txt', otherdata + '/quickie.txt']
with open(otherdata + '/motd.txt', 'w') as outfile:
    for fname in filenames:
        with open(fname) as infile:
            outfile.write(infile.read())

with open(webdata + '/motd.html', 'w') as outfile:
    outfile.write("""
    <style type="text/css" media="screen">
a:link { color:white; }
a:visited { color:white; }
</style>
<link rel="stylesheet" href="../font.css">
    <div class="status" style="padding: 5px;color: white;background:rgba(0,0,0,0.75); font-size: 50%;font-family: minecraftfont;">
                  """)
    for line in open(otherdata + "/motd.txt", "r").readlines():
        outfile.write(showandtellraw.tohtml(line) + "</br>")

    outfile.write('</div>')


with open(webdata + "/status.md", "w") as outfile:
    outfile.write(stats)

