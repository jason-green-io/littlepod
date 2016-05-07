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
name = config['name']
mcversion = config["mcversion"]
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
    

    overmanualpois =  playeroverpoi + overviewer_chestactivity.genpoi('start of day", "-1 days', 'start of day', "o")
    nethermanualpois = playernetherpoi + overviewer_chestactivity.genpoi('start of day", "-1 days', 'start of day', "n")
    endmanualpois =  playerendpoi + overviewer_chestactivity.genpoi('start of day", "-1 days', 'start of day', "e")

else:
    suffix = "latest"
    playeroverpoi, playerovermarker = overviewer_playeractivitydb.genpoimarkers("start of day", "+0 days", "o") 
    playernetherpoi, playernethermarker = overviewer_playeractivitydb.genpoimarkers("start of day", "+0 days", "n")
    playerendpoi, playerendmarker = overviewer_playeractivitydb.genpoimarkers("start of day", "+0 days", "e")
    

    overmanualpois =  playeroverpoi + overviewer_chestactivity.genpoi("start of day", "+0 days", "o")
    nethermanualpois = playernetherpoi + overviewer_chestactivity.genpoi("start of day", "+0 days", "n")
    endmanualpois =  playerendpoi + overviewer_chestactivity.genpoi("start of day", "+0 days", "e")

def pointDict( coords ):
    coordLabel = ("x", "y", "z")
    return dict(zip(coordLabel, coords))

def mcafilter(poi):
    if poi["id"] == "mca":
        # print poi
        return poi

mcapoi = []

for x in xrange(-20, 21):
    for z in xrange(-20, 21):
        x1 = x * 512
        z1 = z * 512
        bl = (x1, 64, z1)
        tl = (x1 + 511, 64, z1)
        tr = (x1 + 511, 64, z1+ 511)
        br = (x1, 64, z1 + 511)

        square = [bl, tl, tr, br, bl]
        poi = dict(text = "r." + str(x) + "." + str(z) + ".mca",
                    id = "mca",
                    color = "red" if (x % 2 or z % 2) else "red",
        
                    x = x1+256,
                     y = 64,
                    z = z1 +256,
                    polyline=tuple([pointDict( coords) for coords in square]))
        mcapoi.append(poi)

markers += [ dict(name="mca file", icon="", filterFunction=mcafilter, createInfoWindow=True, checked=False) ]

overmanualpois += mcapoi
markersOverworld = playerovermarker + markers
markersNether = playernethermarker + markers
markersEnd = playerendmarker + markers


end_smooth_lighting = [Base(), EdgeLines(), SmoothLighting(strength=0.5)]

defaultzoom = 9


texturepath = "/minecraft/host/mcdata/" + mcversion + ".jar"
processes = 1
outputdir = "/minecraft/host/webdata/map/" + mapadminsecret + "/" + suffix + "/"
customwebassets = "/minecraft/host/webdata/map/template"
base = 'http://' + URL + '/map/'


worlds["littlepod"] = "/minecraft/host/otherdata/mcbackup/world"
renders["north"] = {
    "world": name,
    "title": "North",
    "rendermode" : smooth_lighting,
    'dimension' : 'overworld',
    "northdirection" : "upper-left",
    'markers': markersOverworld,
    'base' : base,
    'manualpois' : overmanualpois
}
renders["end"] = {
    "world": name,
    "title": "North",
    "northdirection" : "upper-left",
    'markers': markersEnd ,
    "base" : base,
    'rendermode' : end_smooth_lighting,
    'dimension' : 'end',
    'manualpois' : endmanualpois
}
renders["nether"] = {
    "world": name,
    "title": "North",
    "northdirection" : "upper-left",
    'markers': markersNether ,
    "base" : base,
    'rendermode' : nether,
    'dimension' : 'nether',
    'manualpois' : nethermanualpois
}
