import os
import sys
import time
import datetime

sys.path.append('/minecraft')

import overviewer_chestactivity
import overviewer_playeractivitydb
import yaml


with open('/minecraft/host/config/server.yaml', 'r') as configfile:
    config = yaml.load(configfile)

URL = config['URL']
mapadminsecret = config["mapadminsecret"]


markers = []

markers += overviewer_chestactivity.markers

yesterday = datetime.date.today() - datetime.timedelta(1)

day = 24 * 3600
now = int(time.time())
todayepoch = now - (now % day)
yesterdayepoch = todayepoch - day


if sys.argv[-1] == "yesterday":
    suffix = yesterday.strftime("%Y%m%d")
    playeroverpoi, playerovermarker = overviewer_playeractivitydb.genpoimarkers('start of day", "-1 days', 'start of day', "o") 
    playernetherpoi, playernethermarker = overviewer_playeractivitydb.genpoimarkers('start of day", "-1 days', 'start of day', "n")
    playerendpoi, playerendmarker = overviewer_playeractivitydb.genpoimarkers('start of day", "-1 days', 'start of day', "e")
    

    overmanualpois =  playeroverpoi + overviewer_chestactivity.genpoi("o", yesterdayepoch, todayepoch)
    nethermanualpois = playernetherpoi + overviewer_chestactivity.genpoi("n", yesterdayepoch, todayepoch)
    endmanualpois =  playerendpoi + overviewer_chestactivity.genpoi("e", yesterdayepoch, todayepoch)

else:
    suffix = "latest"
    playeroverpoi, playerovermarker = overviewer_playeractivitydb.genpoimarkers("start of day", "+0 days", "o") 
    playernetherpoi, playernethermarker = overviewer_playeractivitydb.genpoimarkers("start of day", "+0 days", "n")
    playerendpoi, playerendmarker = overviewer_playeractivitydb.genpoimarkers("start of day", "+0 days", "e")
    

    overmanualpois =  playeroverpoi + overviewer_chestactivity.genpoi("o", todayepoch, now)
    nethermanualpois = playernetherpoi + overviewer_chestactivity.genpoi("n", todayepoch, now)
    endmanualpois =  playerendpoi + overviewer_chestactivity.genpoi("e", todayepoch, now)


markersOverworld = playerovermarker + markers
markersNether = playernethermarker + markers
markersEnd = playerendmarker + markers


end_smooth_lighting = [Base(), EdgeLines(), SmoothLighting(strength=0.5)]

defaultzoom = 9

mcversion = "1.8.9"

texturepath = "/minecraft/host/mcdata/" + mcversion + ".jar"
processes = 4
outputdir = "/minecraft/host/webdata/map/" + mapadminsecret + "/" + suffix + "/"
customwebassets = "/minecraft/host/webdata/map/template"
base = 'http://' + URL + '/map/'


worlds["littlepod"] = "/minecraft/host/otherdata/mcbackup/world"
renders["north"] = {
    "world": "littlepod",
    "title": "North",
    "rendermode" : smooth_lighting,
    "northdirection" : "upper-left",
    'markers': markersOverworld,
    'base' : base,
    'manualpois' : overmanualpois
}
renders["end"] = {
    "world": "littlepod",
    "title": "End",
    "northdirection" : "upper-left",
    'markers': markersEnd ,
    "base" : base,
    'rendermode' : end_smooth_lighting,
    'dimension' : 'end',
    'manualpois' : endmanualpois
}
renders["nether"] = {
    "world": "littlepod",
    "title": "Nether",
    "northdirection" : "upper-left",
    'markers': markersNether ,
    "base" : base,
    'rendermode' : nether,
    'dimension' : 'nether',
    'manualpois' : nethermanualpois
}
