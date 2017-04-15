#!/usr/bin/python3 -u
'''
Created on 2014-07-03
'''
import codecs
import threading
import shutil
import sys
import time
import random
import os
import yaml
import sqlite3
import json
import queue
import difflib
from collections import OrderedDict
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
from watchdog.events import FileSystemEventHandler
sys.path.append("/minecraft/NBT")

import nbt
from nbt.nbt import NBTFile, TAG_Long, TAG_Int, TAG_String, TAG_List, TAG_Compound

with open('/minecraft/host/config/server.yaml', 'r') as configfile:
    config = yaml.load(configfile)

mcfolder = config['mcdata']
dbfile = config['dbfile']
otherdata = config["otherdata"]
webdata = config["webdata"]

q = queue.Queue()

def unpack_nbt(tag):
    """                                                                                                                                                                                                          
    Unpack an NBT tag into a native Python data structure.                                                                                                                                                       
    """

    if isinstance(tag, TAG_List):
        return [unpack_nbt(i) for i in tag.tags]
    elif isinstance(tag, TAG_Compound):
        return dict((i.name, unpack_nbt(i)) for i in tag.tags)
    else:
        return tag.value
                    



def writeToDB():
    while True:
        dbQuery(dbfile, 30, q.get())
        q.task_done()

def dbQuery(db, timeout, query):
    con = sqlite3.connect(dbfile)
    results = []

    for x in range(0, timeout):
        try:
            with con:
                cur = con.cursor()

                cur.execute(*query)
                print(query)
                results = cur.fetchall()
        except sqlite3.OperationalError:
            print("Try {} - Locked".format(x))
            time.sleep(random.random())
            pass
        finally:
            break
    else:
        with con:
            cur = con.cursor()
            cur.execute(*query)
            print(query)
            results = cur.fetchall()
                                    
    return results

threadDBWriter = threading.Thread(target=writeToDB)
threadDBWriter.setDaemon(True)
threadDBWriter.start()


def digits(val, digits):
    hi = int(1) << (digits * 4)
        
    uuidPart = hex(hi | (val & (hi-1)))[3:]
    # print(uuidPart)
    return uuidPart

def getUUID(least, most):
    return digits(most >> 32, 8) + "-" + digits(most >> 16, 4) + "-" + digits(most, 4) + "-" + digits(least >> 48, 4) + "-" + digits(least, 12)


def getnbt(filename):
    nbtdata = NBTFile(filename)
    unpackedData = unpack_nbt(nbtdata)
    #print(unpackedData)
    position = unpackedData["Pos"]
    dim = unpackedData["Dimension"]
    inv = unpackedData["Inventory"]
    ender = unpackedData["EnderItems"]
    
    (x1, y1, z1) = tuple(position)
    x1=int(x1)
    y1=int(y1)
    z1 = int(z1)

    def makeLine( item, source ):
        item = dict(item)
        keyFilter = ["Count", "Slot", "id"]
        newItem = OrderedDict()
        newItem.update({"Source": source})
        for key in sorted(item):
            if key in keyFilter:
                newItem.update({key: item[key]})
                if key == "tag":
                    if "display" in item["tag"]:
                        if "Name" in item["tag"]["display"]:
                            item.update({"Name": item["tag"]["display"]["Name"]})

        return json.dumps(newItem)


    invLines = [makeLine(a, "i") for a in inv]
    enderLines = [makeLine(a, "e") for a in ender]

    return (dim, x1, y1, z1, invLines, enderLines)


'''
Extend FileSystemEventHandler to be able to write custom on_any_event method
'''
class FileHandler(PatternMatchingEventHandler):
    '''
    Overwrite the methods for creation, deletion, modification, and moving
    to get more information as to what is happening on output
    '''
    patterns = ["*.dat"]

    def on_moved(self, event):
        if not event.is_directory:
            # time.sleep(1)
            datFile = event.dest_path
            # print(event.src_path, event.dest_path)
            UUID = datFile.split("/")[-1].split(".")[0]
            #try:
            dim, x, y, z, invLines, enderLines = getnbt(datFile)

            #except:
            #    return None


                
            try:
                with open(otherdata + "/items/" + UUID + ".items.txt", "r") as f:
                    oldItems = json.load(f)
            except:
                oldItems = []
                
            newItems = invLines + enderLines
            with codecs.open(otherdata + "/items/" + UUID + ".items.txt", "w", "utf-8") as f:
                json.dump(newItems, f)
            

            # print(newItems, oldItems)
            
            removed = set(oldItems) - set(newItems)
            added = set(newItems) - set(oldItems)
            # print(removed, added)
            removedText = "[{}]".format(", ".join(removed))
            addedText = "[{}]".format(", ".join(added))


            
            # "".join(difflib.ndiff(oldItems, newItems.splitlines(1)))
            # print(html)
            
                


            jsonFile = mcfolder + "/world/stats/" + UUID + ".json"
            pastname = otherdata + "/stats/" + UUID + ".past.json"
            newjson = {} 
            oldjson = {}
            diff = {}

            try:
                with open(pastname, "r") as statfile:
                    oldjson = json.load(statfile)
            except:
                pass
            with open(jsonFile, "r") as statfile:
                newjson = json.load(statfile)
                pass 


            listofstats = list(newjson.keys()) 
            removestats = ["achievement.exploreAllBiomes", "stat.timeSinceDeath", "stat.walkOneCm", "stat.sprintOneCm"]
            for rstat in removestats:
                if rstat in listofstats:
                    listofstats.remove(rstat)
            
            for key in listofstats:
                if int(newjson[key]) > int(oldjson.get(key,"0")):
                    diff.update({key: int(newjson[key]) - int(oldjson.get(key,"0"))})

            if diff:
                pass

            diff = json.dumps(diff)


            shutil.copyfile(jsonFile, pastname)
            q.put(("INSERT INTO playeractivity (UUID, dim, x, y, z, invadded, invremoved, stats) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (UUID, dim, x, y, z, addedText, removedText, diff)))
            # print((UUID, dim, x, y, z, removedText, addedText, diff))

file_watch_directory = mcfolder + "/world/playerdata"       # Get watch_directory parameter


file_event_handler = FileHandler()

file_observer = Observer()
file_observer.schedule(file_event_handler, file_watch_directory, True)

file_observer.start()


'''
Keep the script running or else python closes without stopping the observer
thread and this causes an error.
'''
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    file_observer.stop()


file_observer.join()

