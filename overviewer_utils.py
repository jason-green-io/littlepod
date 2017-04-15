import datetime
import sqlite3
import random
import time
import logging
import json
import Queue
import threading
import yaml

with open('/minecraft/host/config/server.yaml', 'r') as configfile:
    config = yaml.load(configfile)

dbfile = config['dbfile']

now = datetime.datetime.now()
q = Queue.Queue()

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


def dbQuery(db, timeout, query):
    conn = sqlite3.connect(db)
    conn.create_function("diffChest", 2, diffChest)
    conn.create_function("inSphere", 7, inSphere)
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
