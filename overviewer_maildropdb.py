#!/usr/bin/python
import sqlite3
import sys
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

print(curplayers)
print(oldplayers)
print(absentplayers)



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
    if poi['id'] == ('Chest' or "minecraft:chest"):
        if poi.has_key('CustomName'):
            rawplayer = poi['CustomName']
            inverted = True if "!" in rawplayer[0:2] else False
            hidden = rawplayer[0] == "."
            playerdesc = rawplayer.lstrip(".").lstrip('!').split(" ", 1)
            player = playerdesc[0]
    
            desc = playerdesc[1] if len(playerdesc) > 1 else ""

            if player.lower() in players:
                if not hidden:
                    return "{} maildrop\n{}".format(player, desc)


def absentMaildropFilteruniversal( poi, dim, players=absentplayers ):
    if poi['id'] == ('Chest' or "minecraft:chest"):
        if poi.has_key('CustomName'):
            rawplayer = poi['CustomName']
            hidden = rawplayer[0] == ("." or "!")
            inverted = rawplayer[0] == "!"
            playerdesc = rawplayer.lstrip(".").lstrip("!").split(" ", 1)
            player = playerdesc[0]
    
            desc = playerdesc[1] if len(playerdesc) > 1 else ""
            if player.lower() in players:
                
                conn = sqlite3.connect(dbfile)
                cur = conn.cursor()
                # cur.execute('insert into maildrop values (?,?,?,?,?)', (dim + "," + str(poi['x']) + "," + str(poi['y']) + "," + str(poi['z']), player, False, len(poi['Items']), hidden))
                coords = dim + "," + str(poi['x']) + "," + str(poi['y']) + "," + str(poi['z'])
                cur.execute('INSERT OR REPLACE INTO tempmaildrop (coords, name, desc, slots, hidden, inverted ) VALUES (?, ?, ?, ? ,?, ?)', (coords, player, desc, len(poi['Items']), hidden, inverted))
                conn.commit()
                conn.close()
                
                if not (hidden or inverted):                                                                 
                    return "{} maildrop\n{}".format(player, desc)
                


def maildropFilteruniversal( poi, dim, players=curplayers ):

    if poi['id'] == ('Chest' or "minecraft:chest"):
        if poi.has_key('CustomName'):
            rawplayer = poi['CustomName']
            inverted = True if "!" in rawplayer[0:2] else False
            hidden = rawplayer[0] == "."
            playerdesc = rawplayer.lstrip(".").lstrip("!").split(" ", 1)
            player = playerdesc[0]
    
            desc = playerdesc[1] if len(playerdesc) > 1 else ""
            
            if player.lower() in players:

                conn = sqlite3.connect(dbfile)
                cur = conn.cursor()
                # cur.execute('insert into maildrop values (?,?,?,?,?)', (dim + "," + str(poi['x']) + "," + str(poi['y']) + "," + str(poi['z']), player, False, len(poi['Items']), hidden))
                coords = dim + "," + str(poi['x']) + "," + str(poi['y']) + "," + str(poi['z'])
                cur.execute('INSERT OR REPLACE INTO tempmaildrop (coords, name, desc, slots, hidden, inverted ) VALUES (?, ?, ?, ? ,?, ?)', (coords, player, desc, len(poi['Items']), hidden, inverted))
                conn.commit()
                conn.close()


                if not (hidden or inverted):
                    return "{} maildrop\n{}".format(player, desc)
   



markersover = [ dict(name="maildrops (list of shame)", icon="icons/orange/temple_ruins.png", filterFunction=absentMaildropFilterOverworld, checked=True),
               dict(name="maildrops (un-whitelisted)", icon="icons/orange/symbol_blank.png", filterFunction=inactiveMaildropFilterOverworld, checked=True),
               dict(name="maildrops", icon="icons/orange/temple-2.png", filterFunction=maildropFilterOverworld, checked=True) ]
markersnether = [ dict(name="maildrops (list of shame)", icon="icons/orange/temple_ruins.png", filterFunction=absentMaildropFilterNether, checked=True),
                 dict(name="maildrops (un-whitelisted)", icon="icons/orange/symbol_blank.png", filterFunction=inactiveMaildropFilterNether, checked=True),
                 dict(name="maildrops", icon="icons/orange/temple-2.png", filterFunction=maildropFilterNether, checked=True) ]
markersend = [ dict(name="maildrops (list of shame)", icon="icons/ornage/temple_ruins.png", filterFunction=absentMaildropFilterEnd, checked=True),
              dict(name="maildrops (un-whitelisted)", icon="icons/orange/symbol_blank.png", filterFunction=inactiveMaildropFilterEnd, checked=True),
              dict(name="maildrops", icon="icons/orange/temple-2.png", filterFunction=maildropFilterEnd, checked=True) ]

