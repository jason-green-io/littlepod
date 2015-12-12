#!/usr/bin/python
import sqlite3
import sys
sys.path.append('/minecraft')
import vanillabean

dimdict = { "nether" : "2" , "end" : "1", "over" : "0" }


def maildropFilterOverworld(poi):
    return maildropFilteruniversal( poi, "o" )


def maildropFilterNether(poi):
    return maildropFilteruniversal( poi, "n" )


def maildropFilterEnd(poi):
    return maildropFilteruniversal( poi, "e" )


def maildropFilteruniversal( poi, dim ):

    if poi['id'] == 'Chest':
        if poi.has_key('CustomName'):
            rawplayer = poi['CustomName']
            hidden = rawplayer[0] == "."
            player = rawplayer.lstrip(".")
            if player.lower() in vanillabean.getplayers():

                conn = sqlite3.connect('/minecraft/barlynaland.db')
                cur = conn.cursor()
                # cur.execute('insert into maildrop values (?,?,?,?,?)', (dim + "," + str(poi['x']) + "," + str(poi['y']) + "," + str(poi['z']), player, False, len(poi['Items']), hidden))
                coords = dim + "," + str(poi['x']) + "," + str(poi['y']) + "," + str(poi['z'])
                cur.execute('INSERT OR REPLACE INTO maildrop VALUES (?,?,(CASE WHEN (SELECT slots FROM maildrop WHERE coords = ?) == 0 THEN 0 ELSE (SELECT notified FROM maildrop WHERE coords = ?) END) ,?,?)', (coords, player, coords, coords, len(poi['Items']), hidden))
                conn.commit()
                conn.close()


                if not hidden:
                    print player
                    return player + ' maildrop'
    elif poi['id'] == "Sign":
        pass
 # print poi


markersover = [ dict(name="maildrops overworld", icon="icons/black/postal.png", filterFunction=maildropFilterOverworld, checked=True) ]
markersnether = [ dict(name="maildrops nether", icon="icons/black/postal.png", filterFunction=maildropFilterNether, checked=True) ]
markersend = [ dict(name="maildrops end", icon="icons/black/postal.png", filterFunction=maildropFilterEnd, checked=True) ]


