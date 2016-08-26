#!/usr/bin/python
import sqlite3
import sys
import Queue
import threading
sys.path.append('/minecraft')
import vanillabean2
import yaml

with open('/minecraft/host/config/server.yaml', 'r') as configfile:
    config = yaml.load(configfile)


dbfile = config['dbfile']

dimdict = { "nether" : "2" , "end" : "1", "over" : "0" }
conn = sqlite3.connect(dbfile)
cur = conn.cursor()

cur.execute('select name from (select * from joins group by name order by date) where date > datetime("now", "-14 days")')
curplayers = [player[0].lower() for player in cur.fetchall()]

cur.execute('select name from (select * from joins group by name order by date) where date < datetime("now", "-4 months")')
oldplayers = [player[0].lower() for player in cur.fetchall()]

cur.execute('select name from (select * from joins group by name order by date) where date <= datetime("now", "-14 days") and date >= datetime("now", "-4 month")')
absentplayers = [player[0].lower() for player in cur.fetchall()]

conn.commit()
conn.close()

q = Queue.Queue()

def writeToDB():
    global q
    while True:
        DBWriter(q.get())
        q.task_done()


def DBWriter(queryArgs):
    global dbfile
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



threadDBWriter = threading.Thread(target=writeToDB)
threadDBWriter.setDaemon(True)
threadDBWriter.start()

def FilterOverworld(poi):
    return FilterUniversal( poi, "o" )


def FilterNether(poi):
    return FilterUniversal( poi, "n" )


def FilterEnd(poi):
    return FilterUniversal( poi, "e" )



def FilterUniversal( poi, dim ):
    global oldplayers
    global absentplayers
    global curplayers
    if poi['id'] in ['Chest', "minecraft:chest"]:
        if poi.has_key('CustomName'):
            rawplayer = poi['CustomName']
           
            inverted = rawplayer[0] == "!" 
            hidden = rawplayer[0] in [".", "!"]
            playerdesc = rawplayer.lstrip(".").lstrip('!').split(" ", 1)
            player = playerdesc[0]
    
            desc = playerdesc[1] if len(playerdesc) > 1 else ""

            if player.lower() in oldplayers:
                if not hidden:
                    poi["icon"] = "icons/orange/temple_ruins.png"
                    return "{} maildrop\n{}".format(player, desc)


            elif player.lower() in absentplayers:
                
                conn = sqlite3.connect(dbfile)
                cur = conn.cursor()
                # cur.execute('insert into maildrop values (?,?,?,?,?)', (dim + "," + str(poi['x']) + "," + str(poi['y']) + "," + str(poi['z']), player, False, len(poi['Items']), hidden))
                coords = dim + "," + str(poi['x']) + "," + str(poi['y']) + "," + str(poi['z'])
                q.put(('INSERT OR REPLACE INTO tempmaildrop (coords, name, desc, slots, hidden, inverted ) VALUES (?, ?, ?, ? ,?, ?)', (coords, player, desc, len(poi['Items']), hidden, inverted)))
                conn.commit()
                conn.close()
                
                if not (hidden or inverted):
                    poi["icon"] = "icons/orange/symbol_blank.png"
                    return "{} maildrop\n{}".format(player, desc)
                


            elif player.lower() in curplayers:

                conn = sqlite3.connect(dbfile)
                cur = conn.cursor()
                # cur.execute('insert into maildrop values (?,?,?,?,?)', (dim + "," + str(poi['x']) + "," + str(poi['y']) + "," + str(poi['z']), player, False, len(poi['Items']), hidden))
                coords = dim + "," + str(poi['x']) + "," + str(poi['y']) + "," + str(poi['z'])
                q.put(('INSERT OR REPLACE INTO tempmaildrop (coords, name, desc, slots, hidden, inverted ) VALUES (?, ?, ?, ? ,?, ?)', (coords, player, desc, len(poi['Items']), hidden, inverted)))
                conn.commit()
                conn.close()


                if not (hidden or inverted):
                    poi["icon"] = "icons/orange/temple-2.png"
                    return "{} maildrop\n{}".format(player, desc)
   



markersover = [ dict(name="maildrops", icon="icons/orange/temple_ruins.png", filterFunction=FilterOverworld, checked=False)]
markersnether = [ dict(name="maildrops", icon="icons/orange/temple_ruins.png", filterFunction=FilterNether, checked=False)]
markersend = [ dict(name="maildrops", icon="icons/ornage/temple_ruins.png", filterFunction=FilterEnd, checked=False)]


