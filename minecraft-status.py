#!/usr/bin/python

import os
import time
import datetime
import showandtellraw
import sqlite3

servergradient = ["#FFAA00", "#F69900", "#EE8800", "#E57600", "#DD6600", "#D45500", "#CC4400", "#C33300", "#BB2100", "#B21000", "#AA0000", "#970000", "#840000", "#710000", "#5E0000", "#4B0000", "#380000", "#250000", "#120000", "#000000"]
oldgradient = ["#FFAA00", "#F08D00", "#E27100", "#D45500", "#C63800", "#B81C00", "#AA0000", "#880000", "#660000", "#440000", "#210000", "#000000"]
gradient = ["#FFAA00", "#FCA400", "#F99E00", "#F69900", "#F39300", "#F08D00", "#EE8800", "#EB8200", "#E87C00", "#E57600", "#E27100", "#DF6B00", "#DD6600", "#DA6000", "#D75A00", "#D45500", "#D14F00", "#CE4900", "#CC4400", "#C93E00", "#C63800", "#C33300", "#C02D00", "#BD2700", "#BB2100", "#B81C00", "#B51600", "#B21000", "#AF0B00", "#AC0500", "#AA0000", "#A40000", "#9E0000", "#980000", "#920000", "#8C0000", "#860000", "#800000", "#7B0000", "#750000", "#6F0000", "#690000", "#630000", "#5D0000", "#570000", "#520000", "#4C0000", "#460000", "#400000", "#3A0000", "#340000", "#2E0000", "#290000", "#230000", "#1D0000", "#170000", "#110000", "#0B0000", "#050000", "#000000"]


def gengroups(players):
    groupsfinal = ""
    fontstyle = ""
    for player in players:
        # print player
        playername, UUID, lastlogin, status, twitter, twitch, youtube, reddit, maildrop = player

        timediff = datetime.datetime.now() - lastlogin
        s = timediff.seconds
        hours, remainder = divmod(s, 3600)
        minutes, seconds = divmod(remainder, 60)
        last = '%s %02d:%02d' % (timediff.days, hours, minutes)


        social = ""

        if youtube:
            social += '[![youtube](/who/youtube.png)](http://youtube.com/' + youtube + ')'
        if twitter:
            social += '[![twitter](/who/twitter.png)](http://twitter.com/' + twitter + ')'
        if reddit:
            social += '[![reddit](/who/reddit.png)](http://reddit.com/u/' + reddit + ')'
        if twitch:
            social += '[![twitch](/who/twitch.png)](http://twitch.tv/' + twitch + ')'


        # print bool(maildrop)
        playerstatus = maildropstatus = statusstatus = ''
        # print maildropstatus
        if bool(maildrop) or status:
            if bool(maildrop):
                maildropstatus = showandtellraw.tohtml( '<green^Maildrop> for you' )

            if status:
                statusstatus = status
                if bool(maildrop):
                    statusstatus += "</br>"

            playerstatus =  unicode(statusstatus)

        groupsfinal += "|![](https://minotar.net/avatar/" + playername + "/32)|"  + playername  + '|' + social + "|" + playerstatus + "|" + last + "|\n"


    return groupsfinal


def genshame(shame):
    shamefinal =""

    for each in shame:
        lastlogin, playername, UUID, ip = each
        shamefinal += "|" + playername + "|" + str(lastlogin) + "|\n"

    return shamefinal




conn = sqlite3.connect('/minecraft/barlynaland.db', detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
cur = conn.cursor()

cur.execute("SELECT * FROM groups")
players = cur.fetchall()

cur.execute("SELECT * FROM shame")
shame = cur.fetchall()

cur.execute("SELECT * FROM quickie")
quickie = cur.fetchall()

conn.close

statstop = """# Status

## Server message

[gimmick:iframe({height: '120px', width: '100%'})](who/motd.html)

## Last 2 weeks

list of players that have been online in the lest 2 weeks sorted by playtime

|head|player|social|status|last seen (days hh:mm)|
|:-:|:--:|:-:|--|--:|
"""


statsmid = """## Last 24 hours activity

![lag](http://barlynaland.greener.ca/who/stats.png)

## List of shame

list of players that haven't played on the server in over 2 weeks! Shaaaaaame!

|name|last seen|
|-|-:|
"""

stats = statstop + gengroups(players) + statsmid + genshame(shame)

totalminutes = 0
for each in quickie:
    totalminutes += each[1]

totalplayer = len(quickie)


with open("/minecraft/quickie.txt", "w") as outfile:
    line = ("<gold^During the last week ><dark_purple^" +
            str(totalplayer) +
            "><gold^ players played ><dark_purple^" +
            "%.1F" % (totalminutes / 60.0) +
            "><gold^ hours. Average: ><dark_purple^" +
            "%.1F" % (totalminutes / 60.0 / totalplayer) +
            "><gold^ hours per player>")
    print line
    outfile.write(line)

filenames = ['/minecraft/topmotd.txt', '/minecraft/quickie.txt']
with open('/minecraft/motd.txt', 'w') as outfile:
    for fname in filenames:
        with open(fname) as infile:
            outfile.write(infile.read())

with open('/minecraft/web/who/motd.html', 'w') as outfile:
    outfile.write("""
    <style type="text/css" media="screen">
a:link { color:white; }
a:visited { color:white; }
</style>
<link rel="stylesheet" href="../font.css">
    <div class="status" style="padding: 5px;color: white;background:rgba(0,0,0,0.75); font-size: 75%;font-family: minecraftfont;">
                  """)
    for line in open("/minecraft/motd.txt", "r").readlines():
        outfile.write(showandtellraw.tohtml(line) + "</br>")

    outfile.write('</div>')


with open("/minecraft/web/site/status.md", "w") as outfile:
    outfile.write(stats)
