import os
import json
import sys
import pprint
import time
import sqlite3
import yaml
# import overviewer_playeractivity

with open('/minecraft/host/config/server.yaml', 'r') as configfile:
    config = yaml.load(configfile)


mcversion = config['mcversion']    
dbfile = config['dbfile']
name = config['name']
webdata = config["webdata"]

def spawnfilter(poi):
    if poi["id"] == "spawn":
        print poi
        return poi


def poi2text(poi, json=json):
    with file as open(webdata + "/test.md", "a"):
        file.write("|" + "|".join([poi["Text1"], poi["Text2"], poi["Text3"], poi["Text4"]]) + "|")
    return u"\n".join([poi["Text1"], poi["Text2"], poi["Text3"], poi["Text4"]])



def signFilterLocations(poi, poi2text=poi2text):
    if poi['id'] == 'Sign' and "*map*" in poi['Text1']:
     #   print poi2text(poi)
        return poi2text(poi)



def signFilterInactiveBuild(poi, poi2text=poi2text):
    if poi['id'] == 'Sign' and "*home*" in poi['Text1']:
#        print poi2text(poi)
        return poi2text(poi)

def signFilterGrinder(poi, poi2text=poi2text):
    if poi['id'] == 'Sign' and "*grinder*" in poi['Text1']:
 #       print poi2text(poi)
        return poi2text(poi)


Locations = [ dict(name="Locations", icon="icons/black/star-3.png", filterFunction=signFilterLocations, createInfoWindow=True, checked=True) ]


InactiveBuilds =  [ dict(name="Inactive Builds", icon="icons/grey/house.png", filterFunction=signFilterInactiveBuild, createInfoWindow=True, checked=True) ]
Grinder =  [ dict(name="Grinders", icon="icons/black/supermarket.png", filterFunction=signFilterGrinder, createInfoWindow=True, checked=True) ]
spawn =  [ dict(name="Spawn Chunks", icon="", filterFunction=spawnfilter, createInfoWindow=True, checked=False) ]


basic = Locations + InactiveBuilds + Grinder

markersOverworld = [] 
markersEnd = []
markersNether = []



markersEnd += basic
markersNether += basic
markersOverworld += spawn + basic

spawnpoi = [ dict(id="spawn",
                 text="",
                 color="yellow",
                 x=20000,
                 y=64,
                 z=20000,
                 polyline=(dict(x=-320, y=64, z=144),
                           dict(x=-64, y=64, z=144),
                           dict(x=-64,y=64,z=400),
                           dict(x=-320,y=64, z=400),
                           dict(x=-320, y=64, z=144))),
            dict(id="spawn",
                 text="",
                 color="orange",
                 x=20000,
                 y=64,
                 z=20000,
                 polyline=(dict(x=-288, y=64, z=176),
                           dict(x=-96, y=64, z=176),
                           dict(x=-96,y=64,z=368),
                           dict(x=-288,y=64, z=368),
                           dict(x=-288, y=64, z=176)))

]

manualpoisover = []
manualpoisend = []
manualpoisnether = []

manualpoisover += spawnpoi 


if "genPOI" in sys.argv[0]:
    print("Running in genPOI mode, lets load all the things")
    sys.path.append('/minecraft')

    import overviewer_chestactivity
    import overviewer_maildropdb
    import overviewer_transpo
    
    markersOverworld += overviewer_maildropdb.markersover + overviewer_chestactivity.overmarker+ overviewer_transpo.overmarker
    markersEnd += overviewer_maildropdb.markersend + overviewer_chestactivity.endmarker+ overviewer_transpo.endmarker
    markersNether +=  overviewer_maildropdb.markersnether + overviewer_chestactivity.nethermarker+ overviewer_transpo.nethermarker




    polylines = overviewer_transpo.polys()    

    manualpoisover += polylines
    manualpoisend += polylines
    manualpoisnether += polylines


print markersOverworld
print markersEnd
print markersNether

end_smooth_lighting = [Base(), EdgeLines(), SmoothLighting(strength=0.5)]


defaultzoom = 9
showlocationmarker = False


#with open('/minecraft/host/config/mcversion') as versionfile:
#    mcversion = versionfile.readline().strip()

texturepath = "/minecraft/host/mcdata/"+mcversion+".jar"
print texturepath
processes = 1
outputdir = "/minecraft/host/webdata/map"
customwebassets = "/minecraft/host/webdata/map/template"

worlds[name] = '/minecraft/host/otherdata/mcbackup/world'
renders["north"] = {
    "world": name,
    "title": "North",
    "rendermode" : smooth_lighting,
    'dimension' : 'overworld',
    "northdirection" : "upper-left",
    'markers': markersOverworld,
    'manualpois' : manualpoisover
}
renders["end"] = {
    "world": name,
    "title": "North",
    "northdirection" : "upper-left",
    'markers': markersEnd ,
    'rendermode' : end_smooth_lighting,
    'dimension' : 'end',
    'manualpois' : manualpoisend
}
renders["nether"] = {
    "world": name,
    "title": "North",
    "northdirection" : "upper-left",
    'markers': markersNether ,
    'rendermode' : nether,
    'dimension' : 'nether',
    'manualpois' : manualpoisnether
}
