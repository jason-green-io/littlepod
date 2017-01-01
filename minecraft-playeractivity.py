#!/usr/bin/python3 -u
'''
Created on 2014-07-03
'''
import threading
import shutil
import sys
import time
import os
import yaml
import sqlite3
import json
import queue
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
from watchdog.events import FileSystemEventHandler
sys.path.append("/minecraft/NBT")

import nbt

with open('/minecraft/host/config/server.yaml', 'r') as configfile:
    config = yaml.load(configfile)

mcfolder = config['mcdata']
dbfile = config['dbfile']
otherdata = config["otherdata"]

q = queue.Queue()

def writeToDB():
    while True:
        DBWriter(q.get())
        q.task_done()


def DBWriter(queryArgs):
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


def digits(val, digits):
    hi = int(1) << (digits * 4)
        
    uuidPart = hex(hi | (val & (hi-1)))[3:]
    # print(uuidPart)
    return uuidPart

def getUUID(least, most):
    return digits(most >> 32, 8) + "-" + digits(most >> 16, 4) + "-" + digits(most, 4) + "-" + digits(least >> 48, 4) + "-" + digits(least, 12)


def getpos(filename):
    nbtdata = nbt.nbt.NBTFile(filename)
    
    position = [ bla.value for bla in nbtdata["Pos"] ]
    dimension = nbtdata["Dimension"].value
    UUIDleast = nbtdata["UUIDLeast"].value
    UUIDmost = nbtdata["UUIDMost"].value
    # print(UUIDleast, UUIDmost)
    UUID =  getUUID( int(UUIDleast), int(UUIDmost))
    (x1, y1, z1) = tuple(position)
    x1=int(x1)
    y1=int(y1)
    z1 = int(z1)
    dim = dimension
    print((UUID, dim, x1, y1, z1))
    return (UUID, dim, x1, y1, z1)


'''
Extend FileSystemEventHandler to be able to write custom on_any_event method
'''
class PosHandler(PatternMatchingEventHandler):
    '''
    Overwrite the methods for creation, deletion, modification, and moving
    to get more information as to what is happening on output
    '''
    patterns = ["*.dat"]

    def on_moved(self, event):
        if not event.is_directory:
            time.sleep(1)
            filename = event.dest_path
            # print filename
            try:
                pos = getpos(filename)
                # print pos

                q.put(("INSERT INTO location (UUID, dim, x, y, z) VALUES (?,?,?,?,?)", pos))
            except:
                print("File disappeared!")

'''
Extend FileSystemEventHandler to be able to write custom on_any_event method
'''
class StatHandler(FileSystemEventHandler):
    '''
    Overwrite the methods for creation, deletion, modification, and moving
    to get more information as to what is happening on output
    '''

    def on_modified(self, event):
        if not event.is_directory:
            time.sleep(1)
            filename = event.src_path
            # print filename
            
            name = filename.split("/")[-1].split(".")[0]
            pastname = otherdata + "/stats/" + name + ".past.json"
            newjson = {} 
            oldjson = {}
            diff = {}

            try:
                with open(pastname, "r") as statfile:
                    oldjson = json.load(statfile)
            except:
                shutil.copyfile(filename, pastname)
                return

            try:
                with open(filename, "r") as statfile:
                    newjson = json.load(statfile)
            except:
                return 

            listofstats = list(newjson.keys()) 
            removestats = ["achievement.exploreAllBiomes", "stat.timeSinceDeath", "stat.walkOneCm", "stat.sprintOneCm"]
            for rstat in removestats:
                if rstat in listofstats:
                    listofstats.remove(rstat)
            
            for key in listofstats:
                if int(newjson[key]) > int(oldjson.get(key,"0")):
                    diff.update({key: int(newjson[key]) - int(oldjson.get(key,"0"))})

            if diff:
                print(name, diff)

                q.put(("INSERT INTO stats (UUID, stats) VALUES (?,?)", (name, str(diff))))


            shutil.copyfile(filename, pastname)

pos_watch_directory = mcfolder + "/world/playerdata"       # Get watch_directory parameter
stat_watch_directory = mcfolder + "/world/stats"       # Get watch_directory parameter

pos_event_handler = PosHandler()
stat_event_handler = StatHandler()

pos_observer = Observer()
pos_observer.schedule(pos_event_handler, pos_watch_directory, True)

stat_observer = Observer()
stat_observer.schedule(stat_event_handler, stat_watch_directory, True)

pos_observer.start()
stat_observer.start()

'''
Keep the script running or else python closes without stopping the observer
thread and this causes an error.
'''
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    pos_observer.stop()
    stat_observer.stop()

pos_observer.join()
stat_observer.join()
