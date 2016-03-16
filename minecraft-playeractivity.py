#!/usr/bin/python -u
'''
Created on 2014-07-03
'''
import shutil
import sys
import time
import os
import yaml
import nbt2yaml
import sqlite3
import json
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
from watchdog.events import FileSystemEventHandler

with open('/minecraft/host/config/server.yaml', 'r') as configfile:
    config = yaml.load(configfile)

mcfolder = config['mcdata']
dbfile = config['dbfile']
otherdata = config["otherdata"]

def digits(val, digits):
        hi = long(1) << (digits * 4)
        return hex(hi | (val & (hi-1)))[3:-1]


def getUUID(least, most):
        return digits(most >> 32, 8) + "-" + digits(most >> 16, 4) + "-" + digits(most, 4) + "-" + digits(least >> 48, 4) + "-" + digits(least, 12)


def getpos(filename):
    nbt = nbt2yaml.parse_nbt(open( filename, "r" ))
    position = [ bla.data for bla in nbt.data if bla.name == "Pos"]
    dimension = [ bla.data for bla in nbt.data if bla.name == "Dimension"]
    UUIDleast =[ bla.data for bla in nbt.data if bla.name == "UUIDLeast"]
    UUIDmost =[ bla.data for bla in nbt.data if bla.name == "UUIDMost"]
    #print [ tag for tag in nbt ]
    UUID =  getUUID( int(UUIDleast[0]), int(UUIDmost[0]))
    (x1, y1, z1) = position[0][1]
    x1=int(x1)
    y1=int(y1)
    z1 = int(z1)
    dim = dimension[0]
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
            pos = getpos(filename)
            # print pos
            conn = sqlite3.connect(dbfile, timeout=30)
            cur = conn.cursor()
            cur.execute("INSERT INTO location (UUID, dim, x, y, z) VALUES (?,?,?,?,?)", pos)

            conn.commit()
            conn.close()

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
                pass
            with open(filename, "r") as statfile:
                newjson = json.load(statfile)
                pass 
            listofstats = newjson.keys() 
            removestats = ["achievement.exploreAllBiomes", "stat.timeSinceDeath", "stat.playOneMinute", "stat.walkOneCm", "stat.sprintOneCm"]
            for rstat in removestats:
                if rstat in listofstats:
                    listofstats.remove(rstat)
            
            for key in listofstats:
                if int(newjson[key]) > int(oldjson.get(key,"0")):
                    diff.update({key: int(newjson[key]) - int(oldjson.get(key,"0"))})

            if diff:
                print name, diff
                conn = sqlite3.connect(dbfile, timeout=30)
                cur = conn.cursor()
                cur.execute("INSERT INTO stats (UUID, stats) VALUES (?,?)", (name, str(diff)))

                conn.commit()
                conn.close()

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
