import os
import json
import sys
import pprint
import time
sys.path.append('/minecraft')

import overviewer_chestactivity
import overviewer_maildropdb
# import overviewer_playeractivity

def poi2text(poi, json=json):
    return u"\n".join([poi["Text1"], poi["Text2"], poi["Text3"], poi["Text4"]])


def spawnfilter(poi):
    if poi["id"] == "spawn":
        print poi
        return poi

def signFilterLocations(poi, poi2text=poi2text):
    if poi['id'] == 'Sign' and "*map*" in poi['Text1']:
     #   print poi2text(poi)
        return poi2text(poi)

def signFilterredline(poi, poi2text=poi2text):
    if poi['id'] == 'Sign' and "*redline*" in poi['Text1']:
    #    print poi2text(poi)
        return poi2text(poi)

def signFilterpurpleline(poi, poi2text=poi2text):
    if poi['id'] == 'Sign' and "*purpleline*" in poi['Text1']:
    #    print poi2text(poi)
        return poi2text(poi)

def signFilterblueline(poi, poi2text=poi2text):
    if poi['id'] == 'Sign' and "*blueline*" in poi['Text1']:
   #     print poi2text(poi)
        return poi2text(poi)

def signFiltergreenline(poi, poi2text=poi2text):
    if poi['id'] == 'Sign' and "*greenline*" in poi['Text1']:
  #      print poi2text(poi)
        return poi2text(poi)
def signFilteryellowline(poi, poi2text=poi2text):
    if poi['id'] == 'Sign' and "*yellowline*" in poi['Text1']:
 #       print poi2text(poi)
        return poi2text(poi)

def signFilterHome(poi, poi2text=poi2text):
    if poi['id'] == 'Sign' and "*home*" in poi['Text1']:
#        print poi2text(poi)
        return poi2text(poi)

def signFilterGrinder(poi, poi2text=poi2text):
    if poi['id'] == 'Sign' and "*grinder*" in poi['Text1']:
 #       print poi2text(poi)
        return poi2text(poi)


Locations = [ dict(name="Locations", icon="icons/black/star-3.png", filterFunction=signFilterLocations, createInfoWindow=True, checked=True) ]
NetherTrans = [ dict(name="NetherTrans purple", icon="icons/purple/highway.png", filterFunction=signFilterpurpleline, createInfoWindow=True, checked=True),
 dict(name="NetherTrans red", icon="icons/red/highway.png", filterFunction=signFilterredline, createInfoWindow=True, checked=True),
 dict(name="NetherTrans blue", icon="icons/blue/highway.png", filterFunction=signFilterblueline, createInfoWindow=True, checked=True),
 dict(name="NetherTrans green", icon="icons/green/highway.png", filterFunction=signFiltergreenline, createInfoWindow=True, checked=True),
 dict(name="NetherTrans yellow", icon="icons/yellow/highway.png", filterFunction=signFilteryellowline, createInfoWindow=True, checked=True) ]


Home =  [ dict(name="Homes", icon="icons/orange/house.png", filterFunction=signFilterHome, createInfoWindow=True, checked=True) ]
Grinder =  [ dict(name="Grinders", icon="icons/black/supermarket.png", filterFunction=signFilterGrinder, createInfoWindow=True, checked=True) ]
spawn =  [ dict(name="Spawn Chunks", icon="", filterFunction=spawnfilter, createInfoWindow=True, checked=True) ]


markers = spawn + overviewer_chestactivity.markergenerator + Locations + NetherTrans + Home + Grinder

#markers += overviewer_playeractivity.markers
#markers += overviewer_chestactivity.markerdiff

print overviewer_maildropdb.markersover

markersOverworld = markers + overviewer_maildropdb.markersover
markersEnd = markers + overviewer_maildropdb.markersend
markersNether = markers + overviewer_maildropdb.markersnether

spawnpoi = []

manualpois = spawnpoi
end_smooth_lighting = [Base(), EdgeLines(), SmoothLighting(strength=0.5)]

#manualchest = overviewer_chestactivity.diff( "1432992000", "1432993800"  )
#manualchest = overviewer_chestactivity.diff( "", ""  )

defaultzoom = 9

mcversion = "1.8.9"

#with open('/minecraft/host/config/mcversion') as versionfile:
#    mcversion = versionfile.readline().strip()

texturepath = "/minecraft/host/mcdata/" + mcversion + ".jar"
print texturepath
#processes = 1
outputdir = "/minecraft/host/webdata/map"
customwebassets = "/minecraft/host/webdata/map/template"

worlds["littlepod"] = '/minecraft/host/otherdata/mcbackup/world'
renders["north"] = {
    "world": "littlepod",
    "title": "North",
    "rendermode" : smooth_lighting,
    "northdirection" : "upper-left",
    'markers': markersOverworld,
    'manualpois' : manualpois
}
renders["end"] = {
    "world": "littlepod",
    "title": "End",
    "northdirection" : "upper-left",
    'markers': markersEnd ,
    'rendermode' : end_smooth_lighting,
    'dimension' : 'end',
    'manualpois' : ''
}
renders["nether"] = {
    "world": "littlepod",
    "title": "Nether",
    "northdirection" : "upper-left",
    'markers': markersNether ,
    'rendermode' : nether,
    'dimension' : 'nether',
    'manualpois' : ''
}
