#!/usr/bin/python

import vanillabean
import sqlite3
import datetime
import yaml

with open('/minecraft/host/config/server.yaml', 'r') as configfile:
    config = yaml.load(configfile)


dbfile = config['dbfile']

response = vanillabean.send("/list")
numplayers = response.split()[2].split("/")[0]
players = response.strip("'").split(":")[1].split(",")

# response = vanillabean.send("/tp @a ~ ~ ~")
# teleplayers = [(each.split()) for each in response.split("Teleported")]
# print teleplayers
# teleplayers = [(each[0], each[2].strip(','), each[3].strip(','), each[4]) for each in teleplayers if len(each) > 0]
# print teleplayers
conn = sqlite3.connect(dbfile)
cur = conn.cursor()

if int(numplayers) > 0:
    print "Players!"
    for player in players:
        cur.execute('INSERT INTO activity (datetime, name) VALUES (?,?)', (datetime.datetime.now(), player.strip()))

# for location in teleplayers:
#     cur.execute('INSERT INTO location (name, x, y, z) VALUES(?,?,?,?)', location)

conn.commit()
conn.close()
