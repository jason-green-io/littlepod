import os
import json
import sys
import pprint
import time
import sqlite3
import yaml
import codecs
# import overviewer_playeractivity

with open('/minecraft/host/config/server.yaml', 'r') as configfile:
    config = yaml.load(configfile)


mcversion = config['mcversion']    
dbfile = config['dbfile']
name = config['name']
webdata = config["webdata"]
URL = config["URL"]

def spawnfilter(poi):
    if poi["id"] == "spawn":
        print poi
        return poi


def poi2text(poi, dim, codecs=codecs, json=json, dbfile=dbfile, webdata=webdata, URL=URL, sqlite3=sqlite3):

    text = ["Text1", "Text2", "Text3", "Text4"]
    

    for each in text:
        try:
            poi[each] = json.loads(poi[each]).get("text")
            print(poi[each])
        except:
            pass


    conn = sqlite3.connect(dbfile)
    cur = conn.cursor()
    # cur.execute('insert into maildrop values (?,?,?,?,?)', (dim + "," + str(poi['x']) + "," + str(poi['y']) + "," + str(poi['z']), player, False, len(poi['Items']), hidden))
    
    coords = dim + "," + str(poi['x']) + "," + str(poi['y']) + "," + str(poi['z'])
    
    cur.execute('INSERT OR REPLACE INTO pois (coords, type, text1, text2, text3 ) VALUES (?, ?, ?, ? , ?)', (coords, poi["Text1"].strip().strip(u"\uf700"), poi["Text2"], poi["Text3"], poi["Text4"]))
    
    conn.commit()
    conn.close()

    

                                                                                                    

    return u"\n".join([poi["Text1"], poi["Text2"], poi["Text3"], poi["Text4"]])




def signFilterLocations(poi, dim, poi2text=poi2text):
    if poi['id'] in ['Sign', "minecraft:sign"] and "*map*" in poi['Text1']:
     #   print poi2text(poi)
        return poi2text(poi, dim)

def signFilterInactiveBuild(poi, dim, poi2text=poi2text):
    if poi['id'] in ['Sign', "minecraft:sign"] and "*home*" in poi['Text1']:
#        print poi2text(poi)
        return poi2text(poi, dim)

def signFilterShop(poi, dim, poi2text=poi2text):
    if poi['id'] in ['Sign', "minecraft:sign"] and "*shop*" in poi['Text1']:
#        print poi2text(poi)
        return poi2text(poi, dim)

def signFilterGrinder(poi, dim, poi2text=poi2text):
    if poi['id'] in ['Sign', "minecraft:sign"] and ("*grinder*" or "*farm*") in poi['Text1']:
 #       print poi2text(poi)
        poi["Text1"] = "*farm*"
        return poi2text(poi, dim)


def signFilterLocationsOver(poi, poi2text=poi2text, signFilterLocations=signFilterLocations):
    return signFilterLocations(poi, "0")


def signFilterLocationsNether(poi, poi2text=poi2text, signFilterLocations=signFilterLocations):
    return signFilterLocations(poi, "2")


def signFilterLocationsEnd(poi, poi2text=poi2text, signFilterLocations=signFilterLocations):
    return signFilterLocations(poi, "1")


def signFilterInactiveBuildOver(poi, poi2text=poi2text, signFilterInactiveBuild=signFilterInactiveBuild):
    return signFilterInactiveBuild(poi, "0")


def signFilterInactiveBuildNether(poi, poi2text=poi2text, signFilterInactiveBuild=signFilterInactiveBuild):
    return signFilterInactiveBuild(poi, "2")


def signFilterInactiveBuildEnd(poi, poi2text=poi2text, signFilterInactiveBuild=signFilterInactiveBuild):
    return signFilterInactiveBuild(poi, "1")


def signFilterGrinderOver(poi, poi2text=poi2text, signFilterGrinder=signFilterGrinder):
    return signFilterGrinder(poi, "0")


def signFilterGrinderNether(poi, poi2text=poi2text, signFilterGrinder=signFilterGrinder):
    return signFilterGrinder(poi, "2")


def signFilterGrinderEnd(poi, poi2text=poi2text, signFilterGrinder=signFilterGrinder):
    return signFilterGrinder(poi, "1")


def signFilterShopOver(poi, poi2text=poi2text, signFilterShop=signFilterShop):
    return signFilterShop(poi, "0")


def signFilterShopNether(poi, poi2text=poi2text, signFilterShop=signFilterShop):
    return signFilterShop(poi, "2")


def signFilterShopEnd(poi, poi2text=poi2text, signFilterShop=signFilterShop):
    return signFilterShop(poi, "1")




LocationsOver = [ dict(name="Locations Overworld", icon="icons/black/star-3.png", filterFunction=signFilterLocationsOver, createInfoWindow=True, checked=True) ]
LocationsNether = [ dict(name="Locations Nether", icon="icons/black/star-3.png", filterFunction=signFilterLocationsNether, createInfoWindow=True, checked=True) ]
LocationsEnd = [ dict(name="Locations End", icon="icons/black/star-3.png", filterFunction=signFilterLocationsEnd, createInfoWindow=True, checked=True) ]
InactiveBuildsOver =  [ dict(name="Inactive Builds Overworld", icon="icons/grey/house.png", filterFunction=signFilterInactiveBuildOver, createInfoWindow=True, checked=True) ]
InactiveBuildsNether =  [ dict(name="Inactive Builds Nether", icon="icons/grey/house.png", filterFunction=signFilterInactiveBuildNether, createInfoWindow=True, checked=True) ]
InactiveBuildsEnd =  [ dict(name="Inactive Builds End", icon="icons/grey/house.png", filterFunction=signFilterInactiveBuildEnd, createInfoWindow=True, checked=True) ]
GrinderOver =  [ dict(name="Farms Overworld", icon="icons/black/farm2.png", filterFunction=signFilterGrinderOver, createInfoWindow=True, checked=True) ]
GrinderNether =  [ dict(name="Farms Nether", icon="icons/black/farm2.png", filterFunction=signFilterGrinderNether, createInfoWindow=True, checked=True) ]
GrinderEnd =  [ dict(name="Farms End", icon="icons/black/farm2.png", filterFunction=signFilterGrinderEnd, createInfoWindow=True, checked=True) ]

ShopOver =  [ dict(name="Shops Overworld", icon="icons/black/supermarket.png", filterFunction=signFilterShopOver, createInfoWindow=True, checked=True) ]
ShopNether =  [ dict(name="Shops Nether", icon="icons/black/supermarket.png", filterFunction=signFilterShopNether, createInfoWindow=True, checked=True) ]
ShopEnd =  [ dict(name="Shops End", icon="icons/black/supermarket.png", filterFunction=signFilterShopEnd, createInfoWindow=True, checked=True) ]

spawn =  [ dict(name="Spawn Chunks", icon="", filterFunction=spawnfilter, createInfoWindow=True, checked=False) ]



markersOverworld = [] 
markersEnd = []
markersNether = []



markersEnd += LocationsEnd + GrinderEnd + ShopEnd
markersNether += LocationsNether + GrinderNether + ShopNether
markersOverworld += spawn + LocationsOver + GrinderOver + ShopOver

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


# print markersOverworld
# print markersEnd
# print markersNether

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
