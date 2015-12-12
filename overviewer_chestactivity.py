#!/usr/bin/python

import json
import time
import os
import glob

from collections import defaultdict

chestlist = []
otherdata = '/minecraft/host/otherdata'

def chests( poi, chestilist=chestlist ):
    if poi['id'] == 'Chest':
        timenow = int(time.time())
        filetime = timenow - ( timenow % ( 20 * 60 ) )
        #filetime = time.strftime("%Y%m%d%H%M")
        chestfile = otherdata + '/chests/' + str(filetime) + '.json'
        if not os.path.exists(os.path.dirname(chestfile)):
            os.makedirs(os.path.dirname(chestfile))
        with open( chestfile, 'a+' ) as file:

            file.write( json.dumps(poi) + '\n' )


def diff( epoch1, epoch2, day, chestlist=chestlist  ):

    print "Chest activity - Search start:", time.strftime("%Y/%m/%d, %H:%M:%S", time.localtime(int(epoch1))), "end:", time.strftime("%Y/%m/%d, %H:%M:%S", time.localtime(int(epoch2))), "day", day
    if epoch1 == "" and epoch2 == "":
        return []


    files = sorted([file for file in glob.glob(otherdata + "/chests/*.json") if int(file.rsplit('/',1)[1].split('.')[0]) >= epoch1 and int(file.rsplit('/',1)[1].split('.')[0]) <= epoch2 ])

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
        return []




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


chest0 = [ dict(name="Chest Activity - today", icon="icons/black/chest.pngg", filterFunction=filterchest0, createInfoWindow=True, checked=False)]
chest1 = [ dict(name="Chest Activity - yesterday", icon="icons/black/chest.png", filterFunction=filterchest1, createInfoWindow=True, checked=False)]
chest2 = [ dict(name="Chest Activity - 2 days ago", icon="icons/black/chest.png", filterFunction=filterchest2, createInfoWindow=True, checked=False)]
chest3 = [ dict(name="Chest Activity - 3 days ago", icon="icons/black/chest.png", filterFunction=filterchest3, createInfoWindow=True, checked=False)]
chest4 = [ dict(name="Chest Activity - last 31 days", icon="icons/black/chest.png", filterFunction=filterchest4, createInfoWindow=True, checked=False)]


day = 24 * 3600
hour = 60 * 60
twenty = 20 * 60
now = int(time.time())
now = now - (now % twenty) - twenty
todayepoch = now - (now % day)
yesterdayepoch = todayepoch - day
days2agoepoch = yesterdayepoch - day
days3agoepoch = days2agoepoch - day


endrange = 1439438400
range2 = endrange - ( endrange % twenty)

range1 = range2 - 3 * hour


specified = diff( range1, range2, 4 )
days3 = diff( days3agoepoch, days2agoepoch, 3 )
days2 = diff( days2agoepoch, yesterdayepoch, 2 )
yesterday = diff( yesterdayepoch, todayepoch, 1 )
today = diff( todayepoch, now, 0 )


#nether = days3[2] + days2[2] + yesterday[2] + today[2] + specified[2]
#over = days3[1] + days2[1] + yesterday[1] + today[1] + specified[1]
#end = days3[0] + days2[0] + yesterday[0] + today[0] + specified[0]
markers = chest1 + chest2 + chest3 + chest0 + chest4
POIs = specified + days3 + days2 + yesterday + today

markergenerator = [ dict(name="Chest Activity generator", filterFunction=chests, checked=False) ]


# print diff( "1432992000", "1432993800"  )

