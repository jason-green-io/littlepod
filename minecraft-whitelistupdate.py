#!/usr/bin/python3

import yaml
import json
import sqlite3
import vanillabean
import sys
import queue
import threading
import datetime
from pytz import timezone

with open('/minecraft/host/config/server.yaml', 'r') as configfile:
    config = yaml.load(configfile)


dbfile = config['dbfile']
mcfolder = config['mcdata']


whitelist = {each["uuid"]: each["name"] for each in json.load(open(mcfolder + "/whitelist.json"))}
usercache = {each["uuid"]: (datetime.datetime.strptime(each["expiresOn"], "%Y-%m-%d %H:%M:%S %z") - datetime.timedelta(days=30), each["name"]) for each in json.load(open(mcfolder + "/usercache.json"))}

expired = []
active = []
neverseen = []

for each in sorted(usercache, key=usercache.get):
    if each in whitelist.keys() and usercache[each][0] <= datetime.datetime.now(timezone('UTC')) - datetime.timedelta(days=120):
        # print(each, usercache[each])
        expired.append(whitelist[each])

for each in sorted(usercache, key=usercache.get):
    if each in whitelist.keys() and usercache[each][0] > datetime.datetime.now(timezone('UTC')) - datetime.timedelta(days=120):
        # print(each, usercache[each])
        active.append(whitelist[each])


print("Expired ---")
print(expired)
print("Active ---")
print(active)
        

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
                                                                                                

delete = False

if len(sys.argv) > 1:
    delete = True if sys.argv[1] == "delete" else False

for name in expired:
    if delete:
        vanillabean.send("/whitelist remove " + name)
    else:
        print(name)

conn = sqlite3.connect(dbfile)
cur = conn.cursor()

cur.execute("DELETE FROM whitelist")

conn.commit()
conn.close()

whitelist = {each["uuid"]: each["name"] for each in json.load(open(mcfolder + "/whitelist.json"))}

for each in list(whitelist.items()):

    q.put(("INSERT OR IGNORE INTO whitelist (name, UUID) VALUES (?,?)", (each[1], each[0])))


while not q.empty():
    pass
