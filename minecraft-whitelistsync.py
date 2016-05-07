#!/usr/bin/python3


import yaml
import json
import sqlite3
import vanillabean
import sys


with open('/minecraft/host/config/server.yaml', 'r') as configfile:
    config = yaml.load(configfile)


mcfolder = config['mcdata']

sourceFile = sys.argv[1]


whitelistSource = {each["uuid"]: each["name"] for each in json.load(open(sourceFile))}
whitelistDest = {each["uuid"]: each["name"] for each in json.load(open(mcfolder + "/whitelist.json"))}


add = set(whitelistSource.values()) - set(whitelistDest.values())

remove = set(whitelistDest.values()) - set(whitelistSource.values())


for each in add:
    print("/whitelist add {}".format(each))


for each in remove:
    print("/whitelist remove {}".format(each))
