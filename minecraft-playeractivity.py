#!/usr/bin/python
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
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

with open('/minecraft/host/config/server.yaml', 'r') as configfile:
    config = yaml.load(configfile)


dbfile = config['dbfile']


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
class MyHandler(FileSystemEventHandler):
    '''
    Overwrite the methods for creation, deletion, modification, and moving
    to get more information as to what is happening on output
    '''

    def on_moved(self, event):
        time.sleep(1)
        filename = event.dest_path
        print filename
        pos = getpos(filename)
        print pos
        conn = sqlite3.connect(dbfile, timeout=30)
        cur = conn.cursor()
        cur.execute("INSERT INTO location (UUID, dim, x, y, z) VALUES (?,?,?,?,?)", pos)

        conn.commit()
        conn.close()

watch_directory = "/minecraft/world/playerdata"       # Get watch_directory parameter

event_handler = MyHandler()

observer = Observer()
observer.schedule(event_handler, watch_directory, True)
observer.start()

'''
Keep the script running or else python closes without stopping the observer
thread and this causes an error.
'''
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()
observer.join()
