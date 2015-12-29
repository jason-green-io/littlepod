import os
import sys
import time

sys.path.append('/minecraft')

import overviewer_chestactivity
import overviewer_playeractivitydb
import yaml

with open('/minecraft/host/config/server.yaml', 'r') as configfile:
    config = yaml.load(configfile)

URL = config['URL']
mapadminsecret = config["mapadminscret"]

def poi2text(poi):
    text = ["Text1", "Text2", "Text3", "Text4"]
    newtext =[]
   # print poi
    for poitext in text:

        newtext.append(unicode(poi[poitext][1:-1]).encode('UTF-8').decode('unicode-escape'))
    return u"\n".join(newtext)





markers = []

markers += overviewer_playeractivitydb.markers
markers += overviewer_chestactivity.markers

markersOverworld = markers
markersEnd = markers
markersNether = markers

overmanualpois = overviewer_playeractivitydb.overpoi + overviewer_chestactivity.POIs
nethermanualpois = overviewer_playeractivitydb.netherpoi
endmanualpois = overviewer_playeractivitydb.endpoi

end_smooth_lighting = [Base(), EdgeLines(), SmoothLighting(strength=0.5)]

defaultzoom = 9

mcversion = "1.8.9"

texturepath = "/minecraft/host/mcdata/" + mcversion + ".jar"
processes = 1
outputdir = "/minecraft/host/webdata/map/" + mapadminsecret + "/"
customwebassets = "/minecraft/host/webdata/map/template"
base = 'http://' + URL + '/map/'


worlds["littlepod"] = /minecraft/host/otherdata/mcbackup/world
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
