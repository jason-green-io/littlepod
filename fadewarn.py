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
import json
from collections import OrderedDict, defaultdict
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
from watchdog.events import FileSystemEventHandler
import nbt
from nbt.nbt import NBTFile, TAG_Long, TAG_Int, TAG_String, TAG_List, TAG_Compound
import littlepod_utils

mcfolder = os.path.join(os.environ.get('DATAFOLDER', "/minecraft/data"), "mc")
datafolder = os.environ.get("DATAFOLDER")

UUIDtoIGNDict = {player["uuid"]: player["name"] for player in json.load(open(os.path.join(mcfolder, "usercache.json"))) }
print(UUIDtoIGNDict)
safemca = os.environ.get("SAFEMCA")
alert = '{"text":"<<<< warning: fadelands >>>>", "color":"red", "bold": true}'
safemcaDict = defaultdict(list)

for each in safemca.split():
    dim, ranges = each.split("@")
    rangesList = ranges.split(",")

    safemcaDict[int(dim)] += [(x, z) for x in range(int(rangesList[0]), int(rangesList[2]) + 1) for z in range(int(rangesList[1]), int(rangesList[3]) + 1)]

print(safemcaDict)
os.makedirs(os.path.join(datafolder, "seapigeon"), exist_ok=True)

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
            currentmca = (int(newItems["Pos"][0]) >> 9, int(newItems["Pos"][2]) >> 9)
            currentdim = newItems["Dimension"]
            player = UUIDtoIGNDict[UUID]
            if currentmca not in safemcaDict[currentdim]:
                #littlepod_utils.send('/title {player} times 10 200 10\n/title {player} subtitle {alert}\n/title {player} title {{"text":""}}'.format(alert=alert, playaaaer=player))
                littlepod_utils.send('/title {player} actionbar {alert}'.format(alert=alert, player=player))
            else:
                littlepod_utils.send('/title {player} actionbar {"text":"Inside"}')
            print(currentmca, currentdim)



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

