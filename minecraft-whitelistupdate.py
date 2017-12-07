#!/usr/bin/python3
import time
import yaml
import json
import sqlite3
import vanillabean
import sys
import queue
import threading
import datetime
from pytz import timezone

with open('/minecraft/host/config/server.yaml', 'r') as configfile:
    config = yaml.load(configfile)


dbfile = config['dbfile']
mcfolder = config['mcdata']

def getUserCache():
    return {each["uuid"]: (datetime.datetime.strptime(each["expiresOn"], "%Y-%m-%d %H:%M:%S %z") - datetime.timedelta(days=30), each["name"]) for each in json.load(open(mcfolder + "/usercache.json"))}

def getWhitelist():
    return {each["uuid"]: each["name"] for each in json.load(open(mcfolder + "/whitelist.json"))}


def getExpiredPlayers(whitelist=getWhitelist(), usercache=getUserCache()):
    expired = []
    for each in sorted(usercache, key=usercache.get):
        if each in whitelist.keys() and usercache[each][0] <= datetime.datetime.now(timezone('UTC')) - datetime.timedelta(days=120):
            # print(each, usercache[each])
            expired.append(whitelist[each])
    return expired
            
def getActivePlayers(whitelist=getWhitelist(), usercache=getUserCache()):
    active = []
    for each in sorted(usercache, key=usercache.get):
        if each in whitelist.keys() and usercache[each][0] > datetime.datetime.now(timezone('UTC')) - datetime.timedelta(days=120):
            # print(each, usercache[each])
            active.append(whitelist[each])
    return active


        



