#!/usr/bin/python

import os
import re
import json
import time
import gzip
import datetime
import requests
import showandtellraw
import sqlite3

servergradient = ["#FFAA00", "#F69900", "#EE8800", "#E57600", "#DD6600", "#D45500", "#CC4400", "#C33300", "#BB2100", "#B21000", "#AA0000", "#970000", "#840000", "#710000", "#5E0000", "#4B0000", "#380000", "#250000", "#120000", "#000000"]
oldgradient = ["#FFAA00", "#F08D00", "#E27100", "#D45500", "#C63800", "#B81C00", "#AA0000", "#880000", "#660000", "#440000", "#210000", "#000000"]
gradient = ["#FFAA00", "#FCA400", "#F99E00", "#F69900", "#F39300", "#F08D00", "#EE8800", "#EB8200", "#E87C00", "#E57600", "#E27100", "#DF6B00", "#DD6600", "#DA6000", "#D75A00", "#D45500", "#D14F00", "#CE4900", "#CC4400", "#C93E00", "#C63800", "#C33300", "#C02D00", "#BD2700", "#BB2100", "#B81C00", "#B51600", "#B21000", "#AF0B00", "#AC0500", "#AA0000", "#A40000", "#9E0000", "#980000", "#920000", "#8C0000", "#860000", "#800000", "#7B0000", "#750000", "#6F0000", "#690000", "#630000", "#5D0000", "#570000", "#520000", "#4C0000", "#460000", "#400000", "#3A0000", "#340000", "#2E0000", "#290000", "#230000", "#1D0000", "#170000", "#110000", "#0B0000", "#050000", "#000000"]



groupsfinal = []
playertimesfinal = []
shamefinal = []
achievements = []
IP = {}
status = {}
currentplayerlist = [datetime.datetime(1977, 5, 19, 0, 0, 0,), "Dinnerbone"]
historicalplayerlist = {}
numplayers = {}
playeronlinetimes = {}
servernumplayers = []
lag = {}
lagfinal = []
files = []

def genlag(lag, players):
    groups = [ {"options": { "drawPoints": False, "style": "bar", "yAxisOrientation":"right", "barChart": {"width": 10, "align": "right"}}, "id": 1, "content": "players"},
              {"id": 0, "content": "lag", "options": {"drawPoints": False, "style": "bar"}}]
        # {"options": { "drawPoints": False, "style": "bar", "yAxisOrientation":"right", "barChart": {"width": 10, "align": "right"}}, "id": 1, "content": "players"},
    return [groups, [ {"group": 0, "x": point[0], "y": int(point[1])} for point in lag ] + [ {"group": 1, "x": point[0], "y": point[1]} for point in players ]]


def genachievements(achievements):

    achievementstoimg = {
    "Taking Inventory":("Grid_Book.png", False),
    "Getting Wood":("Grid_Oak_Wood.png", False),
    "Benchmarking":("Grid_Crafting_Table.png", False),
    "Time to Mine!":("Grid_Wooden_Pickaxe.png", False),
    "Hot Topic":("Grid_Furnace.png", False),
    "Acquire Hardware":("Grid_Iron_Ingot.png", False),
    "Time to Farm!":("Grid_Wooden_Hoe.png", False),
    "Bake Bread":("Grid_Bread.png", False),
    "The Lie":("Grid_Cake.png", False),
    "Getting an Upgrade":("Grid_Stone_Pickaxe.png", False),
    "Delicious Fish":("Grid_Cooked_Fish.png", False),
    "On A Rail":("Grid_Rail.png", True),
    "Time to Strike!":("Grid_Wooden_Sword.png", False),
    "Monster Hunter":("Grid_Bone.png", False),
    "Cow Tipper":("Grid_Leather.png", False),
    "When Pigs Fly":("Grid_Saddle.png", False),
    "Sniper Duel":("Grid_Bow.png", True),
    "DIAMONDS!":("Grid_Diamond_Ore.png", False),
    "We Need to Go Deeper":("Grid_Obsidian.png", False),
    "Return to Sender":("Grid_Ghast_Tear.png", True),
    "Into Fire":("Grid_Blaze_Rod.png", False),
    "Local Brewery":("Grid_Mundane_Potion.png", False),
    "The End?":("Grid_Eye_of_Ender.png", True),
    "The End.":("Grid_Dragon_Egg.png", True),
    "Enchanter":("Grid_Enchantment_Table.png", False),
    "Overkill":("Grid_Diamond_Sword.png", True),
    "Librarian":("Grid_Bookshelf.png", False),
    "Adventuring Time":("Grid_Diamond_Boots.png", True),
    "The Beginning?":("Grid_Wither_Skeleton_Skull.png", False),
    "The Beginning.":("Grid_Nether_Star.png", False),
    "Beaconator":("Grid_Beacon.png", True),
    "Repopulation":("Grid_Wheat.png", False),
    "Diamonds to you!":("Grid_Diamond.png", False),
    "Overpowered":("Grid_Golden_Apple.png", True)
    }


    achievementsfinal = []


    for achievement in achievements:
        back = "Achievement-fancy.png" if achievementstoimg.get( achievement[2])[1] else "Achievement-plain.png"
        front = achievementstoimg.get( achievement[2])[0]
        start =  achievement[0]
        end = achievement[0]
        achievementsfinal.append( {"style" : "border: 0;background: transparent;",
                                "title" : achievement[2],
                                "type" : "point",
                                "start" : start,
                                "end" : end,
                                "group" : achievement[1],
                                "subgroup" : achievement[1] + "a",
                                "content" : '<div style="display: inline-block; position: relative; width:28px; height:28px;"><div style="position:absolute"><img alt="Achievement-fancy.png" src="img/' + back + '" width="28" height="28" /></div><div style="position:absolute; left:4px; top:4px; line-height:0"><img alt="' + achievement[1] + '" src="img/' + front + '" width="20" height="20" /></div></div>'
    } )

    return achievementsfinal


def genplayeractivity(playeronlinetimes):
    finaltimes = {}
    recentusers = []
    expiredusers =[]
    lastseenusers = {}

    for player in playeronlinetimes:
        therange = False
        timelist = []
        playertimes = sorted(playeronlinetimes[player])
        for t in xrange(len(playertimes)-1):
            if not therange:
                start = playertimes[t]
            if playertimes[t] + datetime.timedelta(0, 5*60) == playertimes[t+1]:
                therange = True
            else:
                end = playertimes[t] + datetime.timedelta(0, 5*60)
                therange = False
                timelist.append( (start, end) )
        if therange:
            timelist.append( (start, playertimes[-1] + datetime.timedelta(0,5*60)) )
        else:
            timelist.append( (playertimes[-1], playertimes[-1]+  datetime.timedelta(0,5*60)) )

        if playertimes[-1] >= datetime.datetime.now() - datetime.timedelta(14) and player in whitelistplayer:
            recentusers.append(playertoUUID.get(player))
            lastseenusers.update( {player: playertimes[-1] } )
        if playertimes[-1] <= datetime.datetime.now() - datetime.timedelta(60) and player in whitelistplayer:
            expiredusers.append(player)

        finaltimes.update( { player : timelist } )

    return finaltimes




# for player in topcountinhour:
#     for times in topcountinhour[player]:
#         if times >= datetime.datetime.now() - datetime.timedelta(14):
#             end = times + datetime.timedelta(0,60*60)
#             print player
#             print playertoUUID.get(player)
#             timeusers.append(  { "style" : "border:0;background-color: " +  gradient[12 - topcountinhour[player][times]] + ";", "type" : "range", "start" : times.isoformat(' '), "end" : end.isoformat(' '), "content" : "", "subgroup" : playertoUUID.get(player) + "ac", "group" :  playertoUUID.get(player) } )
#
#
# topnuminhour = {}
# for times in numplayers:
#     temp = times
#     roundedtohour = temp.replace(minute=0,tzinfo=None)
#     if numplayers[times] > topnuminhour.get(roundedtohour, 0):
#         topnuminhour.update( { roundedtohour: numplayers[times] } )
#
#     #print roundedtohour
#
#
# for times in topnuminhour:
#     if times >= datetime.datetime.now() - datetime.timedelta(14):
#         end = times + datetime.timedelta(0,60*60)
#     #    print topnuminhour[times]
#         if int(topnuminhour[times]) > 0:
#             servernumplayers.append({ "style" : "border:0;background-color: " + servergradient[20 - int(topnuminhour[times])] + ";", "type" : "range", "start" : times.isoformat(' '), "end" : end.isoformat(' '), "content" : '', 'subgroup' : "activity", "group" : "00000-server" })

# for each in lag:
#     if each >= datetime.datetime.now() - datetime.timedelta(14):
#         index =  int(lag[each])/250
#         start = each
#         end = start + datetime.timedelta(0,60*60)
#         if index > 19:
#             index = 19
#
#         lagfinal.append(  { "style" : "border:0;background-color: " +  servergradient[19 - index] + ";", "type" : "range", "start" : start.isoformat(' '), "end" : end.isoformat(' '), "content" : "", "subgroup" : "lag", "group" : "00000-server" } )


# players should be player, UUID, last login, status, maildrop

def genshame(shame):
    global shamefinal
    for each in shame:
        start, name, UUID, ip = each
        shamefinal.append({ "style": "border:0;", "start": start, "content" : name})


def genplayertimes(playertimes):
    global playertimesfinal
    for times in playertimes:
        start, end, UUID, minutes = times
        # print minutes
        playertimesfinal.append(  { "style" : "border:0;background-color: " +  gradient[60 - minutes] + ";", "type" : "range", "start" : start, "end" : end, "content" : "", "subgroup" : UUID + "ac", "group" :  UUID } )


def gengroups(players):
    global groupsfinal
    global onlineplayers
    fontstyle = ""
    for player in players:
        # print player
        playername, UUID, lastlogin, status, twitter, twitch, youtube, reddit, maildrop = player
        if playername in onlineplayers:
            fontstyle = "background-color: #FFAA00; color: white;"
        else:
            timediff = datetime.datetime.now() - lastlogin
            hourspast = int(timediff.total_seconds() // 3600)
            if hourspast > 59:
                hourspast = 59
            fontstyle = "color: " + gradient[ hourspast ] + ";"



        social = ""

        if youtube:
            social += '<a href="http://youtube.com/' + youtube + '"><img src="youtube.png"></a>'
        if twitter:
            social += '<a href="http://twitter.com/' + twitter.strip("@") + '"><img src="twitter.png"></a>'
        if reddit:
            social += '<a href="http://reddit.com/u/' + reddit + '"><img src="reddit.png"></a>'
        if twitch:
            social += '<a href="http://twitch.tv/' + twitch + '"><img src="twitch.png"></a>'


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

            playerstatus =  ' <div class="status" style="padding: 5px;color: white;background:rgba(0,0,0,0.75); font-size: 75%;">' + unicode(statusstatus) + unicode(maildropstatus) + '</div>'

        groupsfinal.append( { "content" : '<div style="padding: 5px; width: 220px; min-height: 60px"> ' + '<div style="width: 100%;' + fontstyle+ '">'+'<img style="height:32px; width:32px; vertical-align:middle" src="https://minotar.net/avatar/' + playername + '/32">  '+ playername +'  </div>' + playerstatus + social + "</div>", "id" : UUID, "sort" : 1})





# players = [("greener_ca", "myUUID", datetime.datetime(2015, 6, 27, 12, 10, 7), "greener_ca", "greener_ca", "greener_ca", "greener_ca", "greener_ca", True)]
# playertimes = [("2015-07-24 07:00:00", "2015-07-24 08:00:00", "6060debe-836f-4a45-95ab-4311a53972f7", 12)]

conn = sqlite3.connect('/minecraft/barlynaland.db', detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
cur = conn.cursor()

cur.execute("SELECT * FROM groups")
players = cur.fetchall()

cur.execute("SELECT * FROM playertimes")
playertimes = cur.fetchall()

cur.execute("SELECT * FROM onlineplayers")
onlineplayers = cur.fetchall()
onlineplayers = [each[0] for each in onlineplayers]

cur.execute("SELECT * FROM shame")
shame = cur.fetchall()

cur.execute("SELECT * FROM lagfinal")
lag = cur.fetchall()

cur.execute("SELECT * from playernum")
playernum = cur.fetchall()

cur.execute("SELECT * from achievementsfinal")
achievements = cur.fetchall()

conn.close
# print players

playertimesfinal = servernumplayers = achievementsfinal = lagfinal = []

achievementsfinal = genachievements(achievements)
# print achievementsfinal
gengroups(players)
# print groupsfinal
genplayertimes(playertimes)
# print playertimesfinal
genshame(shame)
lagfinal = genlag(lag, playernum)
print lagfinal

with open('/minecraft/web/who/motd.html', 'w') as outfile:
    outfile.write("""
    <style type="text/css" media="screen">
a:link { color:white; }
a:visited { color:white; }
</style>
<link rel="stylesheet" href="../font.css">
    <div class="status" style="width: 90%;padding: 5px;color: white;background:rgba(0,0,0,0.75); font-size: 75%;font-family: minecraftfont;">
                  """)
    for line in open("/minecraft/motd.txt", "r").readlines():
        outfile.write(showandtellraw.tohtml(line) + "</br>")

    outfile.write('</div>')

with open('/minecraft/web/who/playeractivity.json', 'w') as outfile:
    json.dump([playertimesfinal + servernumplayers + achievementsfinal + lagfinal, groupsfinal], outfile)

with open('/minecraft/web/who/shame.json', 'w') as outfile:
    json.dump([shamefinal], outfile)

with open('/minecraft/web/who/lag.json', 'w') as outfile:
    json.dump(lagfinal, outfile)
