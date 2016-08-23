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

def maildropFilterOverworld(poi):
    return maildropFilteruniversal( poi, "o" )


def maildropFilterNether(poi):
    return maildropFilteruniversal( poi, "n" )


def maildropFilterEnd(poi):
    return maildropFilteruniversal( poi, "e" )


def inactiveMaildropFilterOverworld(poi):
    return inactiveMaildropFilteruniversal( poi, "o" )


def inactiveMaildropFilterNether(poi):
    return inactiveMaildropFilteruniversal( poi, "n" )


def inactiveMaildropFilterEnd(poi):
    return inactiveMaildropFilteruniversal( poi, "e" )


def absentMaildropFilterOverworld(poi):
    return absentMaildropFilteruniversal( poi, "o" )


def absentMaildropFilterNether(poi):
    return absentMaildropFilteruniversal( poi, "n" )


def absentMaildropFilterEnd(poi):
    return absentMaildropFilteruniversal( poi, "e" )

def inactiveMaildropFilteruniversal( poi, dim, players=oldplayers ):
    if poi['id'] in ['Chest', "minecraft:chest"]:
        if poi.has_key('CustomName'):
            rawplayer = poi['CustomName']
           
            inverted = rawplayer[0] == "!" 
            hidden = rawplayer[0] in [".", "!"]
            playerdesc = rawplayer.lstrip(".").lstrip('!').split(" ", 1)
            player = playerdesc[0]
    
            desc = playerdesc[1] if len(playerdesc) > 1 else ""

            if player.lower() in players:
                if not hidden:
                    return "{} maildrop\n{}".format(player, desc)


def absentMaildropFilteruniversal( poi, dim, players=absentplayers ):
    if poi['id'] in ['Chest', "minecraft:chest"]:
        if poi.has_key('CustomName'):
            rawplayer = poi['CustomName']
            hidden = rawplayer[0] in [".", "!"]
            inverted = rawplayer[0] == "!"
            playerdesc = rawplayer.lstrip(".").lstrip("!").split(" ", 1)
            player = playerdesc[0]
    
            desc = playerdesc[1] if len(playerdesc) > 1 else ""
            if player.lower() in players:
                
                conn = sqlite3.connect(dbfile)
                cur = conn.cursor()
                # cur.execute('insert into maildrop values (?,?,?,?,?)', (dim + "," + str(poi['x']) + "," + str(poi['y']) + "," + str(poi['z']), player, False, len(poi['Items']), hidden))
                coords = dim + "," + str(poi['x']) + "," + str(poi['y']) + "," + str(poi['z'])
                q.put(('INSERT OR REPLACE INTO tempmaildrop (coords, name, desc, slots, hidden, inverted ) VALUES (?, ?, ?, ? ,?, ?)', (coords, player, desc, len(poi['Items']), hidden, inverted)))
                conn.commit()
                conn.close()
                
                if not (hidden or inverted):                                                                 
                    return "{} maildrop\n{}".format(player, desc)
                


def maildropFilteruniversal( poi, dim, players=curplayers ):

    if poi['id'] in ['Chest', "minecraft:chest"]:
        if poi.has_key('CustomName'):
            rawplayer = poi['CustomName']
            inverted = rawplayer[0] == "!"
            hidden = rawplayer[0] in [".", "!"]
            playerdesc = rawplayer.lstrip(".").lstrip("!").split(" ", 1)
            player = playerdesc[0]
    
            desc = playerdesc[1] if len(playerdesc) > 1 else ""
            
            if player.lower() in players:

                conn = sqlite3.connect(dbfile)
                cur = conn.cursor()
                # cur.execute('insert into maildrop values (?,?,?,?,?)', (dim + "," + str(poi['x']) + "," + str(poi['y']) + "," + str(poi['z']), player, False, len(poi['Items']), hidden))
                coords = dim + "," + str(poi['x']) + "," + str(poi['y']) + "," + str(poi['z'])
                q.put(('INSERT OR REPLACE INTO tempmaildrop (coords, name, desc, slots, hidden, inverted ) VALUES (?, ?, ?, ? ,?, ?)', (coords, player, desc, len(poi['Items']), hidden, inverted)))
                conn.commit()
                conn.close()


                if not (hidden or inverted):
                    return "{} maildrop\n{}".format(player, desc)
   



markersover = [ dict(name="maildrops (list of shame)", icon="icons/orange/temple_ruins.png", filterFunction=absentMaildropFilterOverworld, checked=False),
               dict(name="maildrops (un-whitelisted)", icon="icons/orange/symbol_blank.png", filterFunction=inactiveMaildropFilterOverworld, checked=False),
               dict(name="maildrops", icon="icons/orange/temple-2.png", filterFunction=maildropFilterOverworld, checked=False) ]
markersnether = [ dict(name="maildrops (list of shame)", icon="icons/orange/temple_ruins.png", filterFunction=absentMaildropFilterNether, checked=False),
                 dict(name="maildrops (un-whitelisted)", icon="icons/orange/symbol_blank.png", filterFunction=inactiveMaildropFilterNether, checked=False),
                 dict(name="maildrops", icon="icons/orange/temple-2.png", filterFunction=maildropFilterNether, checked=False) ]
markersend = [ dict(name="maildrops (list of shame)", icon="icons/ornage/temple_ruins.png", filterFunction=absentMaildropFilterEnd, checked=False),
              dict(name="maildrops (un-whitelisted)", icon="icons/orange/symbol_blank.png", filterFunction=inactiveMaildropFilterEnd, checked=False),
              dict(name="maildrops", icon="icons/orange/temple-2.png", filterFunction=maildropFilterEnd, checked=False) ]

