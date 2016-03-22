#!/usr/bin/python

import yaml
import json
import sqlite3
import vanillabean

with open('/minecraft/host/config/server.yaml', 'r') as configfile:
    config = yaml.load(configfile)


dbfile = config['dbfile']
mcfolder = config['mcdata']


whitelist = {each["uuid"]: each["name"] for each in json.load(open(mcfolder + "/whitelist.json"))}

# print(whitelist)

conn = sqlite3.connect(dbfile)
cur = conn.cursor()

cur.execute('select name, UUID from (select * from (select * from joins order by date asc) group by UUID) where date > datetime("now", "-4 month") group by UUID')
current = [each[1] for each in cur.fetchall()]

cur.execute('select name, UUID from (select * from (select * from joins order by date asc) group by UUID) group by UUID')
active = [each[1] for each in cur.fetchall()]
# print(current)

cur.execute('select * from whitelist where ts < datetime("now", "-14 days")')
twoWeeksOnList = [each[1] for each in cur.fetchall()]

didntlogin = [each for each in twoWeeksOnList if each not in active]



expired = [each[1] for each in list(whitelist.items()) if each[0] not in current and each[0] in didntlogin]


print(expired)

for name in expired:
    # vanillabean.send("/whitelist remove " + name)
    print(name)



for each in list(whitelist.items()):

    cur.execute("INSERT OR IGNORE INTO whitelist (name, UUID) VALUES (?,?)", (each[1], each[0]))

conn.commit()
conn.close()



