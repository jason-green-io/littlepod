import os
import json
import math
import sys
import pprint
import time
import datetime
import sqlite3
import yaml
import codecs
import Queue
import threading
import random
import atexit
import logging
sys.path.append('/minecraft/')
import overviewer_utils

with open('/minecraft/host/config/server.yaml', 'r') as configfile:
    config = yaml.load(configfile)




mapadminsecret = config["mapadminsecret"]
mcversion = config['mcversion']    
dbfile = config['dbfile']
name = config['name']
webdata = config["webdata"]
URL = config["URL"]

logging.basicConfig(level=logging.DEBUG)


global overviewer_utils

global now
global dbQuery

logging.info(overviewer_utils.now)

now = overviewer_utils.now
dbQuery = overviewer_utils.dbQuery
global timeout
timeout = 120

'''
global reduceItem
def reduceItem( item ):
    from collections import OrderedDict
    import json
    item = dict(item)
    keyFilter = ["Count", "Slot", "id"]
    newItem = OrderedDict()
    
    for key in sorted(item):
        if key in keyFilter:
            newItem.update({key: item[key]})
            if key == "tag":
                if "display" in item["tag"]:
                    if "Name" in item["tag"]["display"]:
                        item.update({"Name": item["tag"]["display"]["Name"]})
                        
    return json.dumps(newItem)

global diffChest
def diffChest(old, new):
    import json
    if old or new:
        Olditems = json.loads(old)
        newItems = json.loads(new)
    
        oldItemsReduced = [reduceItem(item) for item in oldItems]
        newItemsReduced = [reduceItem(item) for item in newItems]
        #print(oldItemsReduced)
        removed = set(oldItemsReduced) - set(newItemsReduced)
        added = set(newItemsReduced) - set(oldItemsReduced)

        removedText = "[{}]".format(", ".join(removed))
        addedText = "[{}]".format(", ".join(added))

        return "[{}, {}]".format(removedText, addedText)
    else:
        return "[[], []]"


global dbQuery
def dbQuery(db, timeout, query):
    global sqlite3
    global random
    global time
    global dbfile
    global logging
    global diffChest
    
    conn = sqlite3.connect(dbfile)
    conn.create_function("diffChest", 2, diffChest)
    results = []
    for x in range(0, timeout):
        try:
            with conn:
                cur = conn.cursor()

                cur.execute(*query)
                # logging.info(query)
                conn.commit()
    
                results = cur.fetchall()

        except sqlite3.OperationalError as e:
            logging.info(query)
            logging.info("Try {} - {}".format(x, e))
            time.sleep(random.random())
            
        
        else:
            break
    else:
        with conn:
            cur = conn.cursor()

            cur.execute(*query)
            # logging.info(query)
            conn.commit()
            results = cur.fetchall()

    return results

global writeToDB
def writeToDB(q):
    logging.info("Setting up writeToDB for config")
    global dbQuery

    while True:
        dbQuery(dbfile, 30, q.get())
        q.task_done()


#threadDBWriter = threading.Thread(target=writeToDB, args=(q,))
#threadDBWriter.setDaemon(True)
#threadDBWriter.start()
'''

global bye
def bye():
    global dbfile
    global time
    logging.info("Resetting tables")


    time.sleep(20)

    # diffChest(chestactivityold.chest, chestactivitynew.chest)
    dbQuery(dbfile, timeout, ('DROP TABLE IF EXISTS pois',))
    dbQuery(dbfile, timeout, ('ALTER TABLE temppois RENAME TO pois',))
    dbQuery(dbfile, timeout, ('CREATE TABLE temppois (coords primary key, type, text1, text2, text3)',))
            
    #dbQuery(dbfile, timeout, ('DROP TABLE IF EXISTS maildrop',))
    #dbQuery(dbfile, timeout, ('ALTER TABLE tempmaildrop RENAME TO maildrop',))
    #dbQuery(dbfile, timeout, ('CREATE TABLE maildrop (coords primary key, name, desc, slots, hidden, inverted, datetime)',))

    dbQuery(dbfile, timeout, ('DROP TABLE IF EXISTS polylines',))
    dbQuery(dbfile, timeout, ('ALTER TABLE temppolylines RENAME TO polylines',))
    dbQuery(dbfile, timeout, ('CREATE TABLE temppolylines (dim, color, id, coords)',))

    dbQuery(dbfile, timeout, ('DROP TABLE IF EXISTS flyway',))
    dbQuery(dbfile, timeout, ('ALTER TABLE tempflyway RENAME TO flyway',))
    dbQuery(dbfile, timeout, ('CREATE TABLE tempflyway (dim, coords, text1, text2, code, destination)',))

    dbQuery(dbfile, timeout, ('DROP TABLE IF EXISTS chestactivityold',))
    dbQuery(dbfile, timeout, ('ALTER TABLE chestactivitynew RENAME TO chestactivityold',))
    dbQuery(dbfile, timeout, ('ALTER TABLE tempchestactivity RENAME TO chestactivitynew',))
    dbQuery(dbfile, timeout, ('CREATE TABLE tempchestactivity (datetime TIMESTAMP, dim, x, y, z, chest)',))

    logging.info("Aaaaaand done.")

    chests = dbQuery(dbfile, timeout, ('INSERT INTO chestactivity SELECT chestactivityold.datetime, chestactivitynew.datetime, dim, x, y, z, diffChest(chestactivityold.chest, chestactivitynew.chest) AS change FROM chestactivityold JOIN chestactivitynew USING (dim, x, y, z) WHERE change != "[[], []]"',))
    
    for each in chests:
        print(each)




markersOverworld = [] 
markersEnd = []
markersNether = []
markersUpper = []

manualpoisover = []
manualpoisend = []
manualpoisnether = []


mode = "general"

if sys.argv[-1].split(",")[0] in ["general", "admin"]:
    logging.info("Running in genPOI mode, lets load all the things")


    global cx, cy, cz, r, start, end
    cx = cy = cz = r = start = end = ""

    try:
        mode, cx, cy, cz, r, start, end = sys.argv[-1].split(",")
        cx = int(cx)
        cy = int(cy)
        cz = int(cz)
        r = int(r)
        
    except:
        pass

    if mode == "general":
        atexit.register(bye)
    logging.info(sys.argv)

    # ======== mca file fliter ========
    def pointDict( coords ):
        coordLabel = ("x", "y", "z")
        return dict(zip(coordLabel, coords))

    def mcafilter(poi):
        if poi["id"] == "mca":
            # print poi
            return poi

    mcapoi = []

    for x in xrange(-20, 21):
        for z in xrange(-20, 21):
            x1 = x * 512
            z1 = z * 512
            bl = (x1, 64, z1)
            tl = (x1 + 511, 64, z1)
            tr = (x1 + 511, 64, z1+ 511)
            br = (x1, 64, z1 + 511)

            square = [bl, tl, tr, br, bl]
            poi = dict(text = "r." + str(x) + "." + str(z) + ".mca",
                        id = "mca",
                        color = "red" if (x % 2 or z % 2) else "red",

                        x = x1+256,
                         y = 64,
                        z = z1 +256,
                        polyline=tuple([pointDict( coords) for coords in square]))
            mcapoi.append(poi)



    # ============= spawn chunks ============

    def spawnfilter(poi):
        if poi["id"] == "spawn":
     
            return poi

    spawnpoi = [ dict(id="spawn",
                     text="",
                     color="orange",
                     x=20000,
                     y=64,
                     z=20000,
                     polyline=(dict(x=-320, y=64, z=144),
                               dict(x=-64, y=64, z=144),
                               dict(x=-64,y=64,z=400),
                               dict(x=-320,y=64, z=400),
                               dict(x=-320, y=64, z=144))),
                dict(id="spawn",
                     text="",
                     color="yellow",
                     x=20000,
                     y=64,
                     z=20000,
                     polyline=(dict(x=-288, y=64, z=176),
                               dict(x=-96, y=64, z=176),
                               dict(x=-96,y=64,z=368),
                               dict(x=-288,y=64, z=368),
                               dict(x=-288, y=64, z=176))),
                dict(id="spawn",
                     text="",
                     color="red",
                     x=20000,
                     y=64,
                     z=20000,
                     polyline=(dict(x=-384, y=64, z=80),
                               dict(x=0, y=64, z=80),
                               dict(x=0,y=64,z=464),
                               dict(x=-384,y=64, z=464),
                               dict(x=-384, y=64, z=80)))

    ]

    # ========== end resources ========

    def endShulkerAndElytra(poi):
        if poi["id"] == "minecraft:shulker":
            poi["icon"] = "icons/endShulker.png"
            return "Shulker"
        elif poi["id"] == "minecraft:item_frame":
            if poi.has_key("Item"):
                if poi["Item"]["id"] == "minecraft:elytra":
                    logging.info(poi)
                    poi["icon"] = "icons/endElytra.png"
                    return "Elytra"
    # =============== pois ===============

    def poi2text(poi, dim):
        global q
        global json
        text = ["Text1", "Text2", "Text3", "Text4"]
    

        for each in text:
            try:
                poi[each] = json.loads(poi[each]).get("text")
                
            except:
                pass
            
        # cur.execute('insert into maildrop values (?,?,?,?,?)', (dim + "," + str(poi['x']) + "," + str(poi['y']) + "," + str(poi['z']), player, False, len(poi['Items']), hidden))
            
        coords = dim + "," + str(poi['x']) + "," + str(poi['y']) + "," + str(poi['z'])
            
        dbQuery(dbfile, timeout, ('INSERT OR REPLACE INTO temppois (coords, type, text1, text2, text3 ) VALUES (?, ?, ?, ? , ?)', (coords, poi["Text1"].strip().strip(u"\uf700"), poi["Text2"], poi["Text3"], poi["Text4"])))
            
            
            
            
            
            
        return u"\n".join([poi["Text1"], poi["Text2"], poi["Text3"], poi["Text4"], str(poi['x']) + " " + str(poi['y']) + " " + str(poi['z'])])
        
        
        
        
    def signFilterLocations(poi, dim, poi2text=poi2text):
        if poi['id'] in ['Sign', "minecraft:sign"] and "*map*" in poi['Text1']:
            #   print poi2text(poi)
            return poi2text(poi, dim)
            
    def signFilterInactiveBuild(poi, dim, poi2text=poi2text):
        if poi['id'] in ['Sign', "minecraft:sign"] and "*home*" in poi['Text1']:
            #        print poi2text(poi)
            return poi2text(poi, dim)
                
    def signFilterShop(poi, dim, poi2text=poi2text):
        if poi['id'] in ['Sign', "minecraft:sign"] and "*shop*" in poi['Text1']:
            #        print poi2text(poi)
            return poi2text(poi, dim)
                    
    def signFilterGrinder(poi, dim, poi2text=poi2text):
        if poi['id'] in ['Sign', "minecraft:sign"] and any(sign in poi['Text1'] for sign in ["*grinder*", "*farm*"]):
            #       print poi2text(poi)
            poi["Text1"] = "*farm*"
            return poi2text(poi, dim)


    def signFilterLocationsOver(poi, poi2text=poi2text, signFilterLocations=signFilterLocations):
        return signFilterLocations(poi, "o")
    

    def signFilterLocationsNether(poi, poi2text=poi2text, signFilterLocations=signFilterLocations):
        return signFilterLocations(poi, "n")


    def signFilterLocationsEnd(poi, poi2text=poi2text, signFilterLocations=signFilterLocations):
        return signFilterLocations(poi, "e")


    def signFilterInactiveBuildOver(poi, poi2text=poi2text, signFilterInactiveBuild=signFilterInactiveBuild):
        return signFilterInactiveBuild(poi, "o")


    def signFilterInactiveBuildNether(poi, poi2text=poi2text, signFilterInactiveBuild=signFilterInactiveBuild):
        return signFilterInactiveBuild(poi, "n")


    def signFilterInactiveBuildEnd(poi, poi2text=poi2text, signFilterInactiveBuild=signFilterInactiveBuild):
        return signFilterInactiveBuild(poi, "e")


    def signFilterGrinderOver(poi, poi2text=poi2text, signFilterGrinder=signFilterGrinder):
        return signFilterGrinder(poi, "o")


    def signFilterGrinderNether(poi, poi2text=poi2text, signFilterGrinder=signFilterGrinder):
        return signFilterGrinder(poi, "n")


    def signFilterGrinderEnd(poi, poi2text=poi2text, signFilterGrinder=signFilterGrinder):
        return signFilterGrinder(poi, "e")


    def signFilterShopOver(poi, poi2text=poi2text, signFilterShop=signFilterShop):
        return signFilterShop(poi, "o")


    def signFilterShopNether(poi, poi2text=poi2text, signFilterShop=signFilterShop):
        return signFilterShop(poi, "n")


    def signFilterShopEnd(poi, poi2text=poi2text, signFilterShop=signFilterShop):
        return signFilterShop(poi, "e")


    def parseCoord( coord ):
        fields = coord.split(',')
        return (int(fields[1]) - 100, int(fields[3]) - 100,  int(fields[1]) + 100, int(fields[3]) + 100)





    # ================ transpo ==================
    global calcBearing
    def calcBearing(coord1, coord2):
        global math
        deltax = coord2[1] - coord1[1] 
        deltaz = coord2[0] - coord1[0]
    
        angle = math.atan2(deltaz, deltax)
        if angle > 0:
            bearing = 180 - 180 / math.pi * angle
        else:
            bearing = -180 - 180 / math.pi * angle

        return bearing



    def genpolys():
        polys = []
        lines = {"purpleline": "purple", "redline": "red", "yellowline": "yellow", "blueline": "blue", "greenline": "green"}
        dim = ["o", "n", "e"]
 

        for d in dim:
        
            routes = dbQuery(dbfile, timeout, ("SELECT a.code, b.code, a.coords, b.coords, a.text1, a.text2 FROM flyway a JOIN flyway b on a.code = b.destination and a.destination = b.code WHERE a.dim = ?", (d,)))
            
            for route in routes:
                logging.info(route)
                polyline = []
                x1, y1, z1 = tuple(route[2].split(","))
                x2, y2, z2 = tuple(route[3].split(","))
                polyline.append({"x": x1, "y": y1,  "z": z1})
                polyline.append({"x": x2, "y": y2,  "z": z2})
                bearing = calcBearing((int(x2),int(z2)),(int(x1),int(z1)))
                distance = math.sqrt(math.fabs(int(x1) -int(x2)) **2 + math.fabs(int(z1)-int(z2)) ** 2 )
                flightLevel = distance / 10+ 10 + int(y2) - int(y1)
                duration = distance / 30
                poly = dict(text = "*flyway*\n{0}\n{1}\n\nfrom {2} to {3}:\nBearing:  {4:.2f}\nFlight level: {5:.0f}\nDuration: {6:.0f}".format(route[4], route[5], route[0], route[1],bearing, flightLevel, duration ),
                            id = "flyway",
                            color = "skyblue",
                            dim = d, 
                            x = x1,
                            y = y1,
                            z = z1,
                            icon = 'icons/skyblue/airport.png',
                            polyline=tuple(polyline)
                )
                polys.append(poly)

            for color in lines:
                coordsFromDB = dbQuery(dbfile, timeout, ("SELECT id, coords FROM polylines WHERE color = ? AND dim = ?", (color, d)))
                coords = sorted(coordsFromDB, key=lambda coord: coord[0]) 
                if coords:
                    polyline = []

                    for each in coords:
                        x, y, z = tuple(each[1].split(","))
                        polyline.append({"x": x, "y": y,  "z": z})

                    poly = dict(text = "",
                                id = "nethertrans",
                                color = lines[color],
                                dim = d, 
                                x = 0,
                                y = 0,
                                z = 0,
                                icon = 'nope',
                                polyline=tuple(polyline)
                    )
                    polys.append(poly)
        

        logging.info(len(polys))
        return polys



    
    global fixText
    def fixText(poi):
     
        lines = ["Text1","Text2","Text3","Text4"]
        for each in lines:
            try:
                poi[each] = json.loads(poi[each]).get("text")
            
            except:
                pass
            poi[each] = poi[each].replace(u"\uf701","").replace(u"\uf700","")
                # print(poi)
        return poi

    global FilterUniversalFlyway
    def FilterUniversalFlyway(poi, dim):
        if poi["id"] == "flyway" and poi["dim"] == dim:
            # print poi
            return poi

        if poi['id'] in ['Sign', "minecraft:sign"]:
            poi = fixText(poi)
            if "*flyway*" in poi['Text1']:
                # print(poi)
                if poi["Text4"]:
                    try:
                        code, destination = tuple(poi["Text4"].split("-"))    
                        if len(code) != 3 and len(destination) != 3:
                            poi["icon"] = "icons/skyblue/airport.png"
                            return poi2text(poi, dim) 
                        
                        dbQuery(dbfile, timeout, ("INSERT INTO tempflyway (dim, coords, text1, text2, code, destination) VALUES (?, ?, ?, ?, ?, ?)",(dim, "{},{},{}".format(poi["x"], poi["y"],poi["z"]), poi["Text2"], poi["Text3"], code, destination )))
                    
                    except:
                        poi["icon"] = "icons/skyblue/airport.png"
                        return poi2text(poi, dim)
            
        
        
    global FilterUniversalNethertrans
    def FilterUniversalNethertrans(poi, dim):
        if poi["id"] == "nethertrans" and poi["dim"] == dim:
            # print poi
            return poi
        
        global poi2text
        lines = {"*purpleline*":"icons/purple/highway.png", "*redline*":"icons/red/highway.png", "*greenline*":"icons/green/highway.png", "*blueline*":"icons/blue/highway.png", "*yellowline*":"icons/yellow/highway.png"}
        if poi['id'] in ['Sign', "minecraft:sign"]:
            poi = fixText(poi)
            if poi["Text1"] in lines.keys():
                # print(poi)
                poi["icon"] = lines[poi["Text1"]]
                if poi["Text4"]:
                    for polyid in poi["Text4"].split(','):
                        try:
                            intid = int(polyid)
                        except:
                            return poi2text(poi, dim) 

                        dbQuery(dbfile, timeout, ("INSERT INTO temppolylines (dim, color, id, coords) VALUES (?, ?, ?, ?)",(dim, poi["Text1"].strip("*"), intid, "{},{},{}".format(poi["x"], poi["y"],poi["z"]))))

                if poi["Text2"] or poi["Text3"]:  
                    
                    return poi2text(poi, dim)

    # Overworld
    def FilterOverNethertrans( poi ):
        return FilterUniversalNethertrans(poi, "o")
    def FilterOverFlyway( poi ):
        return FilterUniversalFlyway(poi, "o")
    
    
    # Nether
    def FilterNetherNethertrans( poi ):
        return FilterUniversalNethertrans(poi, "n")
    def FilterNetherFlyway( poi ):
        return FilterUniversalFlyway(poi, "n")
    
    # End
    def FilterEndNethertrans( poi ):
        return FilterUniversalNethertrans(poi, "e")
    def FilterEndFlyway( poi ):
        return FilterUniversalFlyway(poi, "e")



    # ================ chest activity generator ===============


    def FilterUniversalChests( poi, dim ):
        if (poi['id'] in ['Chest', "minecraft:chest"]) or ("shulker_box" in poi['id']):
            # if "shulker_box" in poi['id']:
                #logging.info(poi)
            x = poi["x"]
            y = poi["y"]
            z = poi["z"]
            content = json.dumps(poi.get("Items", []))
            #filetime = time.strftime("%Y%m%d%H%M")

            dbQuery(dbfile, timeout, ('INSERT INTO tempchestactivity VALUES (?, ?, ?, ?, ?, ?)', (overviewer_utils.now, dim, x, y, z, content)))

            #chestfile = otherdata + '/chests/latest' + "." + dim + '.json'


            #if not os.path.exists(os.path.dirname(chestfile)):
            #    os.makedirs(os.path.dirname(chestfile))
            #with open( chestfile, 'a+' ) as file:

            #    file.write( json.dumps(poi) + '\n' )

    def FilterOverChests(poi):
        global FilterUniversalChests
        return FilterUniversalChests(poi, "o")


    def FilterNetherChests(poi):
        global FilterUniversalChests
        return FilterUniversalChests(poi, "n")


    def FilterEndChests(poi):
        global FilterUniversalChests
        return FilterUniversalChests(poi, "e")



                
    # =============== maildrops ===============


    activePlayersMaildrop = dbQuery(dbfile, timeout, ('select name, ((strftime("%s", date) - strftime("%s", datetime("now", "-112 days"))) / 1209600) from (select * from joins group by name order by date) where date >= datetime("now", "-112 days");',) )

    playersMaildrop = {player[0].lower(): player[1] for player in activePlayersMaildrop}






    def FilterUniversalMaildrop( poi, dim ):
        global playersMaildrop
        global logging
        if poi['id'] in ['Chest', "minecraft:chest"]:
            if poi.has_key('CustomName'):
                rawplayer = poi['CustomName']
                numslots = len(poi['Items'])
                inverted = rawplayer[0] == "!" 
                hidden = rawplayer[0] in [".", "!"]
                playerdesc = rawplayer.lstrip(".").lstrip('!').split(" ", 1)
                player = playerdesc[0]
                
                desc = playerdesc[1] if len(playerdesc) > 1 else ""
                
                iconList = [12, 25, 38, 50, 63, 75, 88, 100] 
                
                if player.lower() in playersMaildrop:
                    weeks = playersMaildrop[player.lower()]
                    
                    if weeks >= 6:
                        # cur.execute('insert into maildrop values (?,?,?,?,?)', (dim + "," + str(poi['x']) + "," + str(poi['y']) + "," + str(poi['z']), player, False, len(poi['Items']), hidden))
                        coords = dim + "," + str(poi['x']) + "," + str(poi['y']) + "," + str(poi['z'])
                        # logging.info(poi)
                        dbQuery(dbfile, timeout, ('INSERT OR IGNORE INTO maildrop (coords, name, desc, slots, hidden, inverted, datetime ) VALUES (?, ?, ?, ? ,?, ?, ?)', (coords, player, desc, numslots, hidden, inverted, now)))
                        dbQuery(dbfile, timeout, ('UPDATE maildrop SET name = ?, desc = ?, slots = ?, hidden = ?, inverted = ? , datetime = ?, notified = CASE WHEN slots <> ? THEN 0 ELSE notified END WHERE coords = ?', (player, desc, numslots, hidden, inverted, now, numslots, coords)))
                        
                        
                        if not (hidden or inverted):
                            poi["icon"] = "icons/orange/{}.png".format(iconList[weeks])
                            return "{} maildrop\n{}\nPlayer last seen approximately {} weeks ago".format(player, desc, 16 - weeks * 2)
                        

    def FilterOverworldMaildrop(poi):
        global FilterUniversalMaildrop
        return FilterUniversalMaildrop( poi, "o" )


    def FilterNetherMaildrop(poi):
        global FilterUniversalMaildrop
        return FilterUniversalMaildrop( poi, "n" )


    def FilterEndMaildrop(poi):
        global FilterUniversalMaildrop
        return FilterUniversalMaildrop( poi, "e" )


    # ======== display chestactivity =======

    def FilterUniversalChestactivity(poi, dim):
        if poi['id'] == 'chestactivity' and poi['dim'] == dim:
            return poi['name']
        

    def FilterOverChestactivity(poi):
        global FilterUniversalChestactivity
        return FilterUniversalChestactivity(poi, "o")

    def FilterNetherChestactivity(poi):
        global FilterUniversalChestactivity
        return FilterUniversalChestactivity(poi, "n")

    def FilterEndChestactivity(poi):
        global FilterUniversalChestactivity
        return FilterUniversalChestactivity(poi, "e")



    def GenerateChest( start, end, dim ):
        print(start, end, dim)
        dimdict = { "o" : "0", "n": "-1", "e": "1"}
        
        data = dbQuery(dbfile, 120, ('SELECT x, y, z, group_concat(datetimestart || "|" || datetimeend || "|" || diff, "||") FROM chestactivity WHERE inSphere(x, y, z, ?, ?, ?, ?) AND (datetimestart BETWEEN ? AND ? OR datetimeend BETWEEN ? AND ?) AND dim == ? GROUP BY dim, x, y, z', (cx, cy, cz, r, start, end, start, end, dim)))
        
        #logging.info(data)
        keys = ("name","x","y","z", "dim")
        pois = []
        chestlist = []
        for chest in data:
            x, y, z, changes = chest
            name = ""
            for change in changes.split("||"):
                # logging.info(change)
                start, end, diff = change.split("|")
                name += start + " to " + end + "</br>"
                
                added, removed = json.loads(diff)
                for item in added:
                    
                    
                    name += "++" + str(item) + "</br>"

                for item in removed:
                    
                    
                    name += "--" + str(item) + "</br>"


            pois.append((name, x, y, z, dim))
        return [dict(zip(keys, poi), id="chestactivity") for poi in pois]

    # =============== player activity ================
    global FilterUniversalPlayers
    def FilterUniversalPlayers(name):
        def filter(poi):
            if poi['id'] == 'player' and poi["name"] == name:
                
                invaddedText = "\n".join(["++" + str(x) for x in json.loads(poi["invadded"])])
                
                invremovedText = "\n".join(["--" + str(x) for x in json.loads(poi["invremoved"])])  
                statsText = "\n".join([str(x) for x in json.loads(poi["stats"]).items()])  

                return "\n".join([poi['name'], poi["datetime"], str(poi['x']) + " " +str(poi['y']) + " " + str(poi['z']), "=== Inventory and Enderchest ===", invaddedText, invremovedText, "=== Stats ===", statsText])
        return filter



    def GeneratePlayers( start, end, dim ):
        print(start, end, dim)



        data = dbQuery(dbfile, 120, ('SELECT datetime, name, x, y, z, invadded, invremoved, stats  FROM playeractivity NATURAL JOIN playerUUID WHERE inSphere(x, y, z, ?, ?, ?, ?) AND datetime BETWEEN ? AND ? AND dim == ?', (cx, cy, cz, r, start, end, dim)))
        
        players = {poi[1] for poi in data}
        keys = ("datetime","name","x","y","z", "invadded", "invremoved", "stats")

        return ([dict(zip(keys, poi), id="player") for poi in data], [dict(checked=True, name="player " + player, icon="https://minotar.net/avatar/"+player+"/16", filterFunction=FilterUniversalPlayers(player)) for player in players])


    

    # ====== all the filters =====
    markersOverChestactivity = [ dict(name="Chest Activity", icon="icons/black/chest.png", filterFunction=FilterOverChestactivity, createInfoWindow=True, checked=True)]
    markersNetherChestactivity = [ dict(name="Chest Activity", icon="icons/black/chest.png", filterFunction=FilterNetherChestactivity, createInfoWindow=True, checked=True)]
    markersEndChestactivity = [ dict(name="Chest Activity", icon="icons/black/chest.png", filterFunction=FilterEndChestactivity, createInfoWindow=True, checked=True)]

    mcafile = [ dict(name="mca file", icon="", filterFunction=mcafilter, createInfoWindow=True, checked=False) ]
    endResources = [ dict(name="Shulkers and Elytras", filterFunction=endShulkerAndElytra, checked=False) ]
    spawnchunks =  [ dict(name="Spawn Chunks", icon="", filterFunction=spawnfilter, createInfoWindow=True, checked=False) ]
    
    LocationsOver = [ dict(name="Locations Overworld", icon="icons/black/star-3.png", filterFunction=signFilterLocationsOver, createInfoWindow=True, checked=True) ]
    LocationsNether = [ dict(name="Locations Nether", icon="icons/black/star-3.png", filterFunction=signFilterLocationsNether, createInfoWindow=True, checked=True) ]
    LocationsEnd = [ dict(name="Locations End", icon="icons/black/star-3.png", filterFunction=signFilterLocationsEnd, createInfoWindow=True, checked=True) ]
    
    InactiveBuildsOver =  [ dict(name="Inactive Builds Overworld", icon="icons/grey/house.png", filterFunction=signFilterInactiveBuildOver, createInfoWindow=True, checked=True) ]
    InactiveBuildsNether =  [ dict(name="Inactive Builds Nether", icon="icons/grey/house.png", filterFunction=signFilterInactiveBuildNether, createInfoWindow=True, checked=True) ]
    InactiveBuildsEnd =  [ dict(name="Inactive Builds End", icon="icons/grey/house.png", filterFunction=signFilterInactiveBuildEnd, createInfoWindow=True, checked=True) ]
    
    GrinderOver =  [ dict(name="Farms Overworld", icon="icons/black/farm2.png", filterFunction=signFilterGrinderOver, createInfoWindow=True, checked=True) ]
    GrinderNether =  [ dict(name="Farms Nether", icon="icons/black/farm2.png", filterFunction=signFilterGrinderNether, createInfoWindow=True, checked=True) ]
    GrinderEnd =  [ dict(name="Farms End", icon="icons/black/farm2.png", filterFunction=signFilterGrinderEnd, createInfoWindow=True, checked=True) ]
    
    ShopOver =  [ dict(name="Shops Overworld", icon="icons/black/supermarket.png", filterFunction=signFilterShopOver, createInfoWindow=True, checked=True) ]
    ShopNether =  [ dict(name="Shops Nether", icon="icons/black/supermarket.png", filterFunction=signFilterShopNether, createInfoWindow=True, checked=True) ]
    ShopEnd =  [ dict(name="Shops End", icon="icons/black/supermarket.png", filterFunction=signFilterShopEnd, createInfoWindow=True, checked=True) ]

    markersOverNethertrans = [ dict(name="nethertrans over", filterFunction=FilterOverNethertrans, createInfoWindow=True, checked=True)]
    markersNetherNethertrans = [ dict(name="nethertrans nether", filterFunction=FilterNetherNethertrans, createInfoWindow=True, checked=True)]
    markersEndNethertrans = [ dict(name="nethertrans end", filterFunction=FilterEndNethertrans, createInfoWindow=True, checked=True)]
    markersUpperNethertrans = [ dict(name="nethertrans nether", filterFunction=FilterNetherNethertrans, createInfoWindow=True, checked=False)]


    markersOverFlyway = [ dict(name="flyway over", filterFunction=FilterOverFlyway, createInfoWindow=True, checked=True)]
    markersNetherFlyway = [ dict(name="flyway nether", filterFunction=FilterNetherFlyway, createInfoWindow=True, checked=False)]
    markersEndFlyway = [ dict(name="flyway end", filterFunction=FilterEndFlyway, createInfoWindow=True, checked=True)]
    markersUpperFlyway = [ dict(name="flyway nether", filterFunction=FilterNetherFlyway, createInfoWindow=True, checked=True)]
    
    
    markersOverChests = [ dict(name="Chest Activity generator over", filterFunction=FilterOverChests, checked=False) ]
    markersNetherChests = [ dict(name="Chest Activity generator nether", filterFunction=FilterNetherChests, checked=False) ]
    markersEndChests = [ dict(name="Chest Activity generator end", filterFunction=FilterEndChests, checked=False) ]

    markersNetherMaildrop = [ dict(name="maildrops", icon="icons/orange/temple_ruins.png", filterFunction=FilterNetherMaildrop, checked=True)]
    markersOverMaildrop = [ dict(name="maildrops", icon="icons/orange/temple_ruins.png", filterFunction=FilterOverworldMaildrop, checked=True)]
    markersEndMaildrop = [ dict(name="maildrops", icon="icons/ornage/temple_ruins.png", filterFunction=FilterEndMaildrop, checked=True)]



    if mode == "admin":
        logging.info("Loading admin filters")
        poisOverPlayers, markersOverPlayers = GeneratePlayers(start, end, 0)
        poisNetherPlayers, markersNetherPlayers = GeneratePlayers(start, end, -1)
        poisEndPlayers, markersEndPlayers = GeneratePlayers(start, end, 1)
                          
        markersOverworld += mcafile + spawnchunks + markersOverChestactivity + markersOverPlayers
        markersNether += markersNetherChestactivity + markersNetherPlayers
        markersEnd += markersEndChestactivity + markersEndPlayers
    elif mode == "general":

        markersUpper += markersNether + LocationsNether + GrinderNether + ShopNether + markersNetherMaildrop + markersUpperFlyway + markersUpperNethertrans + markersNetherChests

        markersEnd += LocationsEnd + GrinderEnd + ShopEnd + markersEndMaildrop + markersEndFlyway + markersEndNethertrans + markersEndChests + endResources
        markersNether += LocationsNether + GrinderNether + ShopNether + markersNetherMaildrop + markersNetherFlyway + markersNetherNethertrans + markersNetherChests
        markersOverworld += spawnchunks + LocationsOver + GrinderOver + ShopOver + markersOverMaildrop + markersOverFlyway + markersOverNethertrans + markersOverChests + mcafile
    # ======== manual markers =====
    if mode == "admin":
        logging.info("Loading admin markers")
        manualpoisover += spawnpoi + mcapoi + GenerateChest(start, end, "o") + poisOverPlayers
        manualpoisnether += GenerateChest(start, end, "n") + poisNetherPlayers
        manualpoisend += GenerateChest(start, end, "e") + poisEndPlayers
    elif mode == "general":
        logging.info("Generating polylines")
        polys = genpolys()

        manualpoisover += polys + spawnpoi + mcapoi
        manualpoisend += polys
        manualpoisnether += polys


end_smooth_lighting = [Base(), EdgeLines(), SmoothLighting(strength=0.5)]
bottom_nether = [Base(), Depth(max=127), EdgeLines(), Nether()]
top_nether = [Base(), Depth(min=127), EdgeLines()]

defaultzoom = 9
showlocationmarker = False



cropAreas=[(-7689, -7227, 8311, 8773)] # + parsedCoords
# print(cropAreas[0:5])

#with open('/minecraft/host/config/mcversion') as versionfile:
#    mcversion = versionfile.readline().strip()

texturepath = "/minecraft/host/mcdata/"+mcversion+".jar"

# logging.info(texturepath)
processes = 4

if mode == "admin":
    outputdir = "/minecraft/host/webdata/map/" + mapadminsecret + "/test"
    base = 'http://' + URL + '/map/'
else:
    outputdir = "/minecraft/host/webdata/map"

customwebassets = "/minecraft/host/webdata/map/template"

title = "North"

worlds[name] = '/minecraft/host/otherdata/mcbackup/world'

renders["overworld"] = {
    "world": name,
    "title": "Overworld",
    "rendermode" : smooth_lighting,
    'dimension' : 'overworld',
    "northdirection" : "upper-left",
    'markers': markersOverworld,
    'manualpois' : manualpoisover,
    'crop': cropAreas
}
renders["end"] = {
    "world": name,
    "title": "End",
    "northdirection" : "upper-left",
    'markers': markersEnd ,
    'rendermode' : end_smooth_lighting,
    'dimension' : 'end',
    'manualpois' : manualpoisend
}
renders["nether"] = {
    "world": name,
    "title": "Nether",
    "northdirection" : "upper-left",
    'markers': markersNether ,
    'rendermode' : bottom_nether,
    'dimension' : 'nether',
    'manualpois' : manualpoisnether
}
renders["upper"] = {
    "world": name,
    "title": "Upper",
    "northdirection" : "upper-left",
    'markers': markersUpper ,
    'rendermode' : top_nether,
    'dimension' : 'nether',
    'manualpois' : manualpoisnether
}
