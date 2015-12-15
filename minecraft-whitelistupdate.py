#!/usr/bin/python

import yaml
import json
import sqlite3
import vanillabean

with open('/minecraft/host/config/server.yaml', 'r') as configfile:
    config = yaml.load(configfile)


dbfile = config['dbfile']
mcfolder = config['mcfolder']

conn = sqlite3.connect(dbfile)
cur = conn.cursor()

cur.execute('select name from (select * from (select * from joins order by date asc) group by UUID) natural join whitelist where date < datetime("now", "-4 month") group by name')
expired = cur.fetchall()

print expired

for name in expired:
    vanillabean.send("/whitelist remove " + name[0])

whitelist = [(each["name"], each["uuid"]) for each in json.load(open(mcfolder + "/whitelist.json"))]

cur.execute("DROP TABLE whitelist")
cur.execute("CREATE TABLE whitelist (name, uuid)")
for each in whitelist:

    cur.execute("INSERT OR REPLACE INTO whitelist VALUES (?,?)", each)

conn.commit()
conn.close()



