#!/usr/bin/python
import sqlite3
import sys
sys.path.append('/minecraft')
import vanillabean
import yaml

with open('/minecraft/host/config/server.yaml', 'r') as configfile:
    config = yaml.load(configfile)


dbfile = config['dbfile']

dimdict = { "nether" : "2" , "end" : "1", "over" : "0" }
conn = sqlite3.connect(dbfile)
cur = conn.cursor()
cur.execute('select name from (select * from joins group by name order by date) where date > datetime("now", "-6 months")')
curplayers = [player[0].lower() for player in cur.fetchall()]

cur.execute('select name from (select * from joins group by name order by date) where date <= datetime("now", "-6 months")')
oldplayers = [player[0].lower() for player in cur.fetchall()]
conn.commit()
conn.close()


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


def inactiveMaildropFilteruniversal( poi, dim, players=oldplayers ):
    if poi['id'] == 'Chest':
        if poi.has_key('CustomName'):
            rawplayer = poi['CustomName']
            hidden = rawplayer[0] == "."
            player = rawplayer.lstrip(".")
            if player.lower() in players:
                if not hidden:
                    return player + ' maildrop'




def maildropFilteruniversal( poi, dim, players=curplayers ):

    if poi['id'] == 'Chest':
        if poi.has_key('CustomName'):
            rawplayer = poi['CustomName']
            hidden = rawplayer[0] == "."
            player = rawplayer.lstrip(".")
            if player.lower() in players:

                conn = sqlite3.connect(dbfile)
                cur = conn.cursor()
                # cur.execute('insert into maildrop values (?,?,?,?,?)', (dim + "," + str(poi['x']) + "," + str(poi['y']) + "," + str(poi['z']), player, False, len(poi['Items']), hidden))
                coords = dim + "," + str(poi['x']) + "," + str(poi['y']) + "," + str(poi['z'])
                cur.execute('INSERT OR REPLACE INTO maildrop (coords, name, notified, slots, hidden )VALUES (?,?,(CASE WHEN (SELECT slots FROM maildrop WHERE coords = ?) == 0 THEN 0 ELSE (SELECT notified FROM maildrop WHERE coords = ?) END) ,?,?)', (coords, player, coords, coords, len(poi['Items']), hidden))
                conn.commit()
                conn.close()


                if not hidden:
                    return player + ' maildrop'
    elif poi['id'] == "Sign":
        pass
 # print poi


markersover = [ dict(name="inactive maildrops overworld", icon="icons/grey/house.png", filterFunction=inactiveMaildropFilterOverworld, checked=True),
               dict(name="maildrops overworld", icon="icons/orange/house.png", filterFunction=maildropFilterOverworld, checked=True) ]
markersnether = [ dict(name="inactive maildrops nether", icon="icons/grey/house.png", filterFunction=inactiveMaildropFilterNether, checked=True),
                 dict(name="maildrops nether", icon="icons/orange/house.png", filterFunction=maildropFilterNether, checked=True) ]
markersend = [ dict(name="maildrops end", icon="icons/grey/house.png", filterFunction=inactiveMaildropFilterEnd, checked=True),
              dict(name="maildrops end", icon="icons/orange/house.png", filterFunction=maildropFilterEnd, checked=True) ]


