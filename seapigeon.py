#!/usr/bin/python3 -u
import codecs
import datetime
import time
import os
import json
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler, FileSystemEventHandler
import nbtlib
import pymongo

mcfolder = os.path.join(os.environ.get('DATAFOLDER', "/data"), "mc")
datafolder = os.environ.get("DATAFOLDER")

client = pymongo.MongoClient("tesseract_mongo_1")

db = client["testing"]

col = db["seapigeon"]

class FileHandler(PatternMatchingEventHandler):
    '''
    Overwrite the methods for creation, deletion, modification, and moving
    to get more information as to what is happening on output
    '''
    patterns = ["*.dat"]

    def on_moved(self, event):
        if not event.is_directory:

            datFile = event.dest_path

            UUID = datFile.split("/")[-1].split(".")[0]
            timeNow =  datetime.datetime.now()
            nbtFile = nbtlib.load(datFile)
            nbt = nbtFile.root
            insert = {"UUID": UUID, "time": timeNow}
            insert.update(nbt)
            _id = col.insert_one(insert)
            print(_id)

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

