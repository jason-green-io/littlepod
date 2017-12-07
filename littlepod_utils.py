import datetime
import sqlite3
import random
import time
import logging
import json
import requests

try: import Queue
except ImportError:
    try: import queue as Queue
    except:
        print("Bad news")
import threading
import yaml

with open('/minecraft/host/config/server.yaml', 'r') as configfile:
    config = yaml.load(configfile)


name = config['name']
dbfile = config['dbfile']
mcfolder = config['mcdata']
URL = config['URL']
webdata = config['webdata']

now = datetime.datetime.now()
q = Queue.Queue()


def getUserCache():
    return {each["uuid"]: (datetime.datetime.strptime(each["expiresOn"][:19], "%Y-%m-%d %H:%M:%S") - datetime.timedelta(days=30), each["name"]) for each in json.load(open(mcfolder + "/usercache.json"))}

def getWhitelist():
    return {each["uuid"]: each["name"] for each in json.load(open(mcfolder + "/whitelist.json"))}

def getWhitelistByIGN():
    return {each["name"].lower(): each["uuid"] for each in json.load(open(mcfolder + "/whitelist.json"))}

def getNameFromAPI(uuid):
    return requests.get('https://api.mojang.com/user/profiles/{}/names'.format(uuid.replace('-', ''))).json()[-1].get("name", "")

def getPlayerStatus(whitelist=getWhitelist(), usercache=getUserCache()):
    expired = []
    active = []
    for each in sorted(usercache, key=usercache.get):
        if each in whitelist and usercache[each][0] <= datetime.datetime.now() - datetime.timedelta(days=120):
            # print(each, usercache[each])
            expired.append(each)
    

    for each in sorted(usercache, key=usercache.get):
        if each in whitelist and usercache[each][0] > datetime.datetime.now() - datetime.timedelta(days=120):
            # print(each, usercache[each])
            active.append(each)
    return {"active": active, "expired": expired}
                                                


                                        



def reduceItem( item ):
    from collections import OrderedDict
    item = dict(item)
    keyFilter = ["Count", "Slot", "id"]
    newItem = OrderedDict()
    
    for key in sorted(item):
        if key in keyFilter:
            newItem.update({key: item[key]})
            if key == "tag":
                if "display" in item["tag"]:
                    if "Name" in item["tag"]["display"]:
                        item.update({"Name": item["tag"]["display"]["Name"]})
                        
    return json.dumps(newItem)


def diffChest(old, new):
    if old or new:
        oldItems = json.loads(old)
        newItems = json.loads(new)
    
        oldItemsReduced = [reduceItem(item) for item in oldItems]
        newItemsReduced = [reduceItem(item) for item in newItems]
        #print(oldItemsReduced)
        removed = set(oldItemsReduced) - set(newItemsReduced)
        added = set(newItemsReduced) - set(oldItemsReduced)

        removedText = "[{}]".format(", ".join(removed))
        addedText = "[{}]".format(", ".join(added))

        return "[{}, {}]".format(removedText, addedText)
    else:
        return "[[], []]"

def inSphere(x, y, z, cx, cy, cz, r):
    if x or y or z:
        return (x - cx) ** 2 + (y - cy) ** 2 + (z - cz) ** 2 < r ** 2

def getStat(stats, stat):

        if stats:
            evalStats = eval(stats)

            if type(evalStats) is dict:
                return evalStats.get(stat, 0)

            
            



def dbQuery(db, timeout, query):
    conn = sqlite3.connect(db, detect_types=sqlite3.PARSE_COLNAMES)
    conn.create_function("diffChest", 2, diffChest)
    conn.create_function("inSphere", 7, inSphere)
    conn.create_function("getStat", 2, getStat)
    results = []
    for x in range(0, timeout):
        try:
            with conn:
                cur = conn.cursor()

                cur.execute(*query)
                # logging.info(query)
                conn.commit()
    
                results = cur.fetchall()

        except sqlite3.OperationalError as e:
            logging.info(query)
            logging.info("Try {} - {}".format(x, e))
            time.sleep(random.random())
            
        
        else:
            break
    else:
        with conn:
            cur = conn.cursor()

            cur.execute(*query)
            # logging.info(query)
            conn.commit()
            results = cur.fetchall()

    return results


def writeToDB(queue):
    logging.info("Setting up writeToDB for config")


    while True:
        dbQuery(dbfile, 30, queue.get())
        q.task_done()


threadDBWriter = threading.Thread(target=writeToDB, args=(q,))
threadDBWriter.setDaemon(True)
threadDBWriter.start()
