#!/usr/bin/python -u
import paho.mqtt.client as paho
import requests
import socket
import ssl
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

from nbt.nbt import NBTFile, TAG_Long, TAG_Int, TAG_String, TAG_List, TAG_Compound

# load some server config stuff (this is from littlepod, the server wrapper)
with open('/minecraft/host/config/server.yaml', 'r') as configfile:
    config = yaml.load(configfile)

mcfolder = config['mcdata']
dbfile = config['dbfile']
otherdata = config["otherdata"]

level = []
scoreboard = []



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

    
def nbt_to_object(filename):
    ''' return an object from an NBT file'''
    nbtData = NBTFile(filename)

    return unpack_nbt(nbtData)


# start a queue for database stuff
q = queue.Queue()


def writeToDB():
    ''' execute a query, and wait for the next one  '''
    while True:
        DBWriter(q.get())
        q.task_done()


def DBWriter(queryArgs):
    ''' spin on database locks  '''
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

# start the database stuff
threadDBWriter = threading.Thread(target=writeToDB)
threadDBWriter.setDaemon(True)
threadDBWriter.start()



connflag = False

def on_connect(client, userdata, flags, rc):
    ''' connect to AWS IoT  '''
    global connflag
    connflag = True
    print("Connection returned result: " + str(rc) )

def on_message(client, userdata, msg):
    ''' publish a message to a topic  '''
    print(msg.topic+" "+str(msg.payload))
"""
# set some paho stuff
mqttc = paho.Client()
mqttc.on_connect = on_connect
mqttc.on_message = on_message

# if you're using this code, you'll need to change this stuff
awshost = "data.iot.eu-west-1.amazonaws.com"
awsport = 8883
clientId = "barlynaland"
thingName = "barlynaland"
caPath = "aws-iot-rootCA.crt"
certPath = "7b5fede5e4-certificate.pem.crt"
keyPath = "7b5fede5e4-private.pem.key"

mqttc.tls_set(caPath, certfile=certPath, keyfile=keyPath, cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1_2, ciphers=None)

mqttc.connect(awshost, awsport, keepalive=60)

# start the thread to publish
mqttc.loop_start()

"""

class LevelHandler(PatternMatchingEventHandler):
#class FileHandler(FileSystemEventHandler):
    '''
    Overwrite the methods for creation, deletion, modification, and moving
    to get more information as to what is happening on output
    '''
    patterns = ["*/level.dat"]
    
    def on_moved(self, event):
        ''' listen to changes in level.dat  '''
        if not event.is_directory and event.dest_path.endswith("level.dat"):
            time.sleep(1)
            filename = event.dest_path
            # get the level.dat as a python object
            level = nbt_to_object(filename)
            # letus know something happened
            print("Moved", event.src_path, event.dest_path)
            # go get the server total ticks, and modulo 24000 to get days and ticks in the day
            serverDayTime = divmod(level["Data"]["DayTime"], 24000)
            # send it to the cloud, AWS IoT
            print(serverDayTime)
            r = requests.post("https://twopenny-pika-4720.dataplicity.io/mctime", params={"serverTime": serverDayTime[1], "moonPhase": divmod(serverDayTime[0], 8)[1]})
            print(r.text)
class ScoreboardHandler(PatternMatchingEventHandler):
    '''
    Overwrite the methods for creation, deletion, modification, and moving
    to get more information as to what is happening on output
    '''
    patterns = ["*/scoreboard.dat"]
    
    def on_modified(self, event):
        ''' listen for changes to the scorboard  '''
        if not event.is_directory:
            time.sleep(1)
            filename = event.src_path
            scoreboard = nbt_to_object(filename)

            print("Modified", filename)
            print([team["Players"] for team in scoreboard["data"]["Teams"] if team["Name"] == "mute"])
            

            
file_watch_directory = mcfolder + "/world/"       # Get watch_directory parameter

# get the handlers ready
level_event_handler = LevelHandler()
scoreboard_event_handler = ScoreboardHandler()

# start them up
level_observer = Observer()
level_observer.schedule(level_event_handler, file_watch_directory, True)

scoreboard_observer = Observer()
scoreboard_observer.schedule(scoreboard_event_handler, file_watch_directory, True)

level_observer.start()
scoreboard_observer.start()

'''
Keep the script running or else python closes without stopping the observer
thread and this causes an error.
'''
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    level_observer.stop()
    scoreboard_observer.stop()

level_observer.join()
scoreboard_observer.join()
