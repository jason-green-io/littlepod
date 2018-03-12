#!/usr/bin/python3 -u
'''
Created on 2014-07-03
'''
import codecs
import threading
import shutil
import sys
import datetime
import time
import os
import yaml
import json
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
otherdata = config["otherdata"]




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
                    


def getnbt(filename):
    nbtdata = NBTFile(filename)
    return unpack_nbt(nbtdata)


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

            datFile = event.dest_path

            UUID = datFile.split("/")[-1].split(".")[0]
            
            newItems = getnbt(datFile)
            print(datFile)
            with codecs.open(otherdata + "/seapigeon/" + UUID + "." + str(datetime.datetime.now().strftime('%Y%m%d%H%M%S')) + ".json", "w", "utf-8") as f:
                json.dump(newItems, f)
            

            

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

