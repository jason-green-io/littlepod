#!/usr/bin/python
'''
Created on 2014-07-03
'''
import shutil
import sys
import time
import os

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

'''
Extend FileSystemEventHandler to be able to write custom on_any_event method
'''
class MyHandler(FileSystemEventHandler):
    '''
    Overwrite the methods for creation, deletion, modification, and moving
    to get more information as to what is happening on output
    '''
    def on_moved(self, event):
        uuid = event.dest_path.split("/")[-1].split('.')[0]
        newfolder = "/minecraft/god/" + uuid
        newfile = newfolder + "/" + str(int( time.time() )) + ".dat"
        print( time.time(), uuid )
        if not os.path.exists( newfolder ):
            os.makedirs( newfolder )
        try:
            shutil.copyfile( event.dest_path, newfile )
        except:
            pass

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
