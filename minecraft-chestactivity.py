#!/usr/bin/python3
import json
import sqlite3
import yaml
import glob
import os
import queue
import threading
from collections import defaultdict

with open('/minecraft/host/config/server.yaml', 'r') as configfile:
    config = yaml.load(configfile)


dbfile = config['dbfile']

latestfile = "/minecraft/host/otherdata/chests/latest" 
oldfile = "/minecraft/host/otherdata/chests/old"


dimlist = ["o", "n", "e"]




files = glob.glob(latestfile + "*") + glob.glob(oldfile + "*")


q = queue.Queue()

def writeToDB():
    global q
    while True:
        DBWriter(q.get())
        q.task_done()


def DBWriter(queryArgs):
    global dbfile
    conn = sqlite3.connect(dbfile)
    cur = conn.cursor()
    
    fail = True
    while(fail):
        try:
            cur.execute(*queryArgs)
            conn.commit()
            fail = False
        except sqlite3.OperationalError:
            print("Locked")
            fail = True
            

        
threadDBWriter = threading.Thread(target=writeToDB)
threadDBWriter.setDaemon(True)
threadDBWriter.start()
                                                                                                




if not files:
    print("There are no files!")
    exit()
    
if len(files) != 6:
    print("Files are missing!" )
    exit()


for each in dimlist:
    print(each)
    oldchestlist = [ json.loads( chest.strip() ) for chest in open(oldfile + "." + each + ".json", 'r').readlines() if "LootTable" not in chest ]
    chestlist = [ json.loads( chest.strip() ) for chest in open(latestfile + "." + each + ".json", 'r').readlines() if "LootTable" not in chest]


    chestlistcompare = {}
    oldchestlistcompare = {}


    for chest in chestlist:
        # print chest
        total = defaultdict( int )
        for item in chest["Items"]:
            total[ item["id"] ] += item["Count"]

        chestlistcompare.update( { (str(chest[ "x" ]), str(chest[ "y" ]), str(chest[ "z" ]), itemid ) : itemcount for itemid, itemcount in total.items() } )

    # print chestlistcompare

    for chest in oldchestlist:
        total = defaultdict( int )

        for item in chest["Items"]:
            total[ item["id"] ] += item["Count"]

        oldchestlistcompare.update( { (str(chest[ "x" ]), str(chest[ "y" ]), str(chest[ "z" ]), itemid ) : itemcount for itemid, itemcount in total.items() } )

    # print(oldchestlistcompare)

    diff = set( chestlistcompare.items() ) ^ set( oldchestlistcompare.items() )

    diffdict = defaultdict( dict)

    for changes in set( [ x[0] for x in diff] ):
        # print([each] + list(changes[0:3]))
        itemname = str(changes[3]).split(":")[-1]
        if changes in chestlistcompare and changes in oldchestlistcompare:
            diffdict[ ",".join([each] + list(changes[0:3])) ].update( { itemname : chestlistcompare[ changes ] - oldchestlistcompare[ changes ] })

        elif changes not in chestlistcompare:
            diffdict[ ",".join([each] + list(changes[0:3])) ].update( { itemname : - oldchestlistcompare[ changes ]})

        elif changes not in oldchestlistcompare:
            diffdict[ ",".join([each] + list(changes[0:3])) ].update( { itemname : chestlistcompare[ changes ]})

    
    for each in diffdict.items():
        q.put(('INSERT INTO chests (coords, chest) VALUES (?, ?)', (each[0], json.dumps(each[1]))))
        print( each[0], json.dumps(each[1]) )


    # return [ { "id": "chestactivity" + str(day), "x" : chest[0][0], "y" : chest[0][1],  "z" : chest[0][2], "contents" : "\n".join(chest[1]) } for chest in diffdict.items() ]



for each in dimlist:
    os.rename(latestfile + "." + each + ".json", oldfile + "." + each + ".json")
