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


chest0 = [ dict(name="Chest Activity - today", icon="icons/black/chest.png", filterFunction=filterchest0, createInfoWindow=True, checked=True)]




def genpoi(dim, start, end):

    return diff( start, end, 0, dim)


markers = chest0

overmarker = [ dict(name="Chest Activity generator over", filterFunction=chestsOverworld, checked=False) ]
nethermarker = [ dict(name="Chest Activity generator nether", filterFunction=chestsNether, checked=False) ]
endmarker = [ dict(name="Chest Activity generator end", filterFunction=chestsEnd, checked=False) ]



