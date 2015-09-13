import os
import json
import sys
import pprint
import time
sys.path.append('/minecraft')

import overviewer_chestactivity
import overviewer_maildropdb
# import overviewer_playeractivity
import something
import tmux
import showandtellraw
#import overviewer-chests

def poi2text(poi, json=json):
    text = ["Text1", "Text2", "Text3", "Text4"]
    newtext =[]
    print poi

    for poitext in text:
        parsedjson = json.loads(poi[poitext])
        print repr(parsedjson)
        if type(parsedjson) == unicode:
            newtext.append(parsedjson)
        else:
            newtext.append(parsedjson["text"])
    return u"\n".join(newtext)



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



markers = overviewer_chestactivity.markergenerator + Locations + NetherTrans + Home + Grinder

#markers += overviewer_playeractivity.markers
#markers += overviewer_chestactivity.markerdiff

print overviewer_maildropdb.markersover

markersOverworld = markers + overviewer_maildropdb.markersover
markersEnd = markers + overviewer_maildropdb.markersend
markersNether = markers + overviewer_maildropdb.markersnether

manualchest = ''


end_smooth_lighting = [Base(), EdgeLines(), SmoothLighting(strength=0.5)]

#manualchest = overviewer_chestactivity.diff( "1432992000", "1432993800"  )
#manualchest = overviewer_chestactivity.diff( "", ""  )

defaultzoom = 9

texturepath = "/minecraft/1.8.jar"
processes = 1
outputdir = "/minecraft/web/map"
customwebassets = "/minecraft/web/map/template"
snapshotpath = "/minecraft/worlddisk/.zfs/snapshot"

snapshots = os.listdir( snapshotpath )
snapshots.remove( 'latest' )

latestsnapshot = snapshotpath + '/' + max(snapshots)

print latestsnapshot
worlds["Barlynaland"] = latestsnapshot
renders["north"] = {
    "world": "Barlynaland",
    "title": "North",
    "rendermode" : smooth_lighting,
    "northdirection" : "upper-left",
    'markers': markersOverworld,
    'manualpois' : ''
}
renders["east"] = {
    "world": "Barlynaland",
    "title": "East",
    "rendermode" : smooth_lighting,
    "northdirection" : "lower-left",
    'markers': markersOverworld,
    'manualpois' : manualchest
}
renders["south"] = {
    "world": "Barlynaland",
    "title": "South",
    "rendermode" : smooth_lighting,
    "northdirection" : "lower-right",
    'markers': markersOverworld,
    'manualpois' : manualchest
}
renders["west"] = {
    "world": "Barlynaland",
    "title": "West",
    "rendermode" : smooth_lighting,
    "northdirection" : "upper-right",
    'markers': markersOverworld,
    'manualpois' : manualchest
}
renders["end"] = {
    "world": "Barlynaland",
    "title": "End",
    "northdirection" : "upper-left",
    'markers': markersEnd ,
    'rendermode' : end_smooth_lighting,
    'dimension' : 'end',
    'manualpois' : ''
}
renders["nether"] = {
    "world": "Barlynaland",
    "title": "Nether",
    "northdirection" : "upper-left",
    'markers': markersNether ,
    'rendermode' : nether,
    'dimension' : 'nether',
    'manualpois' : ''
}
