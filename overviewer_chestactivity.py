#!/usr/bin/python

import json
import time
import os
import glob

from collections import defaultdict

chestlist = []
otherdata = '/minecraft/host/otherdata'

timenow = int(time.time())
filetime = timenow


def chestsOverworld(poi, filetime=filetime):
    return chestsUniversal(poi, "o", filetime)


def chestsNether(poi, filetime=filetime):
    return chestsUniversal(poi, "n", filetime)


def chestsEnd(poi, filetime=filetime):
    return chestsUniversal(poi, "e", filetime)

def chestsUniversal( poi, dim, filetime ):
    if poi['id'] == 'Chest':
        
        #filetime = time.strftime("%Y%m%d%H%M")
        chestfile = otherdata + '/chests/' + str(filetime) + "." + dim + '.json'
        if not os.path.exists(os.path.dirname(chestfile)):
            os.makedirs(os.path.dirname(chestfile))
        with open( chestfile, 'a+' ) as file:

            file.write( json.dumps(poi) + '\n' )


def diff( epoch1, epoch2, day, dim ):
    POIs = []

    print "Chest activity " + dim + " - Search start:", time.strftime("%Y/%m/%d, %H:%M:%S", time.localtime(int(epoch1))), "end:", time.strftime("%Y/%m/%d, %H:%M:%S", time.localtime(int(epoch2))), "day", day
    if epoch1 == "" and epoch2 == "":
        return POIs


    files = sorted([file for file in glob.glob(otherdata + "/chests/*." + dim + ".json") if int(file.rsplit('/',1)[1].split('.')[0]) >= epoch1 and int(file.rsplit('/',1)[1].split('.')[0]) <= epoch2 ])

    print files
    try:
        fileepoch1 = files[0]
        fileepoch2 = files[-1]
        print "Found  start:", time.strftime("%Y/%m/%d, %H:%M:%S", time.localtime(int(fileepoch1.rsplit('/',1)[1].split('.')[0]))), "end:", time.strftime("%Y/%m/%d, %H:%M:%S", time.localtime(int(fileepoch2.rsplit('/',1)[1].split('.')[0])))
        print fileepoch1, fileepoch2

        epoch1missing = not os.path.exists( fileepoch1 )
        epoch2missing = not os.path.exists( fileepoch2 )
    except:
        pass
        print "files missing, skipping"
        return POIs




    oldchestlist = [ json.loads( chest.strip() ) for chest in open(fileepoch1, 'r').readlines() if "LootTable" not in chest ]
    chestlist = [ json.loads( chest.strip() ) for chest in open(fileepoch2, 'r').readlines() if "LootTable" not in chest]


    chestlistcompare = {}
    oldchestlistcompare = {}


    for chest in chestlist:
    #    print chest
        total = defaultdict( int )
        for item in chest["Items"]:
            total[ item["id"] ] += item["Count"]

        chestlistcompare.update( { (chest[ "x" ], chest[ "y" ], chest[ "z" ], itemid ) : itemcount for itemid, itemcount in total.items() } )

    #print chestlistcompare

    for chest in oldchestlist:
        total = defaultdict( int )

        for item in chest["Items"]:
            total[ item["id"] ] += item["Count"]

        oldchestlistcompare.update( { (chest[ "x" ], chest[ "y" ], chest[ "z" ], itemid ) : itemcount for itemid, itemcount in total.items() } )



    diff = set( chestlistcompare.items() ) ^ set( oldchestlistcompare.items() )

    diffdict = defaultdict( list)

    for changes in set( [ x[0] for x in diff] ):
        if changes in chestlistcompare and changes in oldchestlistcompare:
            diffdict[ changes[0:3] ] += [ str(changes[3]).split(":")[-1] + " " +str(chestlistcompare[ changes ] - oldchestlistcompare[ changes ]) ]
        elif changes not in chestlistcompare:
            diffdict[ changes[0:3]] += [ str(changes[3]).split(":")[-1] + " " +str(- oldchestlistcompare[ changes ]) ]

        elif changes not in oldchestlistcompare:

            diffdict[changes[0:3]]+=[ str(changes[3]).split(":")[-1]+ " " +str(chestlistcompare[ changes ]) ]

    return [ { "id": "chestactivity" + str(day), "x" : chest[0][0], "y" : chest[0][1],  "z" : chest[0][2], "contents" : "\n".join(chest[1]) } for chest in diffdict.items() ]

def filterchest0(poi):
    if poi['id'] == 'chestactivity0':
        return poi['contents']


def filterchest1(poi):
    if poi['id'] == 'chestactivity1':
        return poi['contents']


def filterchest2(poi):
    if poi['id'] == 'chestactivity2':
        return poi['contents']


def filterchest3(poi):
    if poi['id'] == 'chestactivity3':
        return poi['contents']


def filterchest4(poi):
    if poi['id'] == 'chestactivity4':
        return poi['contents']




chest0 = [ dict(name="Chest Activity - today", icon="icons/black/chest.png", filterFunction=filterchest0, createInfoWindow=True, checked=False)]
chest1 = [ dict(name="Chest Activity - yesterday", icon="icons/black/chest.png", filterFunction=filterchest1, createInfoWindow=True, checked=False)]
chest2 = [ dict(name="Chest Activity - 2 days ago", icon="icons/black/chest.png", filterFunction=filterchest2, createInfoWindow=True, checked=False)]
chest3 = [ dict(name="Chest Activity - 3 days ago", icon="icons/black/chest.png", filterFunction=filterchest3, createInfoWindow=True, checked=False)]
chest4 = [ dict(name="Chest Activity - last 31 days", icon="icons/black/chest.png", filterFunction=filterchest4, createInfoWindow=True, checked=False)]



day = 24 * 3600
hour = 60 * 60
twenty = 20 * 60
now = int(time.time())
now = now 
todayepoch = now - (now % day)
yesterdayepoch = todayepoch - day
days2agoepoch = yesterdayepoch - day
days3agoepoch = days2agoepoch - day


endrange = 1439438400
range2 = endrange - ( endrange % twenty)

range1 = range2 - 3 * hour


ospecified = diff( range1, range2, 4, "o" )
odays3 = diff( days3agoepoch, days2agoepoch, 3, "o" )
odays2 = diff( days2agoepoch, yesterdayepoch, 2, "o" )
oyesterday = diff( yesterdayepoch, todayepoch, 1, "o" )
otoday = diff( todayepoch, now, 0, "o" )

nspecified = diff( range1, range2, 4, "n" )
ndays3 = diff( days3agoepoch, days2agoepoch, 3, "n" )
ndays2 = diff( days2agoepoch, yesterdayepoch, 2, "n" )
nyesterday = diff( yesterdayepoch, todayepoch, 1, "n" )
ntoday = diff( todayepoch, now, 0, "n" )

especified = diff( range1, range2, 4, "e" )
edays3 = diff( days3agoepoch, days2agoepoch, 3, "e" )
edays2 = diff( days2agoepoch, yesterdayepoch, 2, "e" )
eyesterday = diff( yesterdayepoch, todayepoch, 1, "e" )
etoday = diff( todayepoch, now, 0, "e" )

markers = chest1 + chest2 + chest3 + chest0 + chest4

overpoi = ospecified + odays3 + odays2 + oyesterday + otoday
netherpoi = nspecified + ndays3 + ndays2 + nyesterday + ntoday
endpoi = especified + edays3 + edays2 + eyesterday + etoday

print endpoi

overmarker = [ dict(name="Chest Activity generator over", filterFunction=chestsOverworld, checked=False) ]
nethermarker = [ dict(name="Chest Activity generator nether", filterFunction=chestsNether, checked=False) ]
endmarker = [ dict(name="Chest Activity generator end", filterFunction=chestsEnd, checked=False) ]



