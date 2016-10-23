import json
import sqlite3
import yaml
import math
import Queue
import threading

with open('/minecraft/host/config/server.yaml', 'r') as configfile:
    config = yaml.load(configfile)


dbfile = config['dbfile']

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
                                                                                                


def calcBearing(coord1, coord2):
    deltax = coord2[1] - coord1[1] 
    deltaz = coord2[0] - coord1[0]
    
    angle = math.atan2(deltaz, deltax)
    if angle > 0:
        bearing = 180 - 180 / math.pi * angle
    else:
        bearing = -180 - 180 / math.pi * angle

    return bearing





def polys():
    polys = []
    lines = {"purpleline": "purple", "redline": "red", "yellowline": "yellow", "blueline": "blue", "greenline": "green"}
    dim = ["o", "n", "e"]
    conn = sqlite3.connect(dbfile)
    cur = conn.cursor()

    for d in dim:
        
        cur.execute("SELECT a.code, b.code, a.coords, b.coords, a.text1, a.text2 FROM flyway a JOIN flyway b on a.code = b.destination and a.destination = b.code WHERE a.dim = ?", (d,))
        routes = cur.fetchall()
        for route in routes:
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
                        id = "transpo",
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
            cur.execute("SELECT id, coords FROM polylines WHERE color = ? AND dim = ?", (color, d))
            coords = sorted(cur.fetchall(), key=lambda coord: coord[0]) 
            if coords:
                polyline = []

                for each in coords:
                    x, y, z = tuple(each[1].split(","))
                    polyline.append({"x": x, "y": y,  "z": z})

                poly = dict(text = "",
                            id = "transpo",
                            color = lines[color],
                            dim = d, 
                            x = 0,
                            y = 0,
                            z = 0,
                            icon = 'nope',
                            polyline=tuple(polyline)
                            )
                polys.append(poly)

    cur.execute("DELETE FROM polylines")
    cur.execute("DELETE FROM flyway")
    conn.commit()
    conn.close()


    return polys


def poi2text(poi, json=json):
    return u"\n".join([poi["Text1"], poi["Text2"], poi["Text3"], poi["Text4"]])


# Overworld
def FilterOver( poi ):
    return FilterUniversal(poi, "o")


# Nether
def FilterNether( poi ):
    return FilterUniversal(poi, "n")

# End
def FilterEnd( poi ):
    return FilterUniversal(poi, "e")


def fixText(poi):
    global json
    lines = ["Text1","Text2","Text3","Text4"]
    for each in lines:
        try:
            poi[each] = json.loads(poi[each]).get("text")
            
        except:
            pass
        poi[each] = poi[each].replace(u"\uf701","").replace(u"\uf700","")
    print(poi)
    return poi
    

def FilterUniversal(poi, dim):
    if poi["id"] == "transpo" and poi["dim"] == dim:
        # print poi
        return poi

    global poi2text
    lines = {"*purpleline*":"icons/purple/highway.png", "*redline*":"icons/red/highway.png", "*greenline*":"icons/green/highway.png", "*blueline*":"icons/blue/highway.png", "*yellowline*":"icons/yellow/highway.png"}
    if poi['id'] in ['Sign', "minecraft:sign"]:
        poi = fixText(poi)
        if "*flyway*" in poi['Text1']:
            # print(poi)
            if poi["Text4"]:
                try:
                    code, destination = tuple(poi["Text4"].split("-"))    
                    if len(code) != 3 and len(destination) != 3:
                        poi["icon"] = "icons/skyblue/airport.png"
                        return poi2text(poi) 
                    #conn = sqlite3.connect(dbfile)
                    #cur = conn.cursor()
                    q.put(("INSERT INTO flyway (dim, coords, text1, text2, code, destination) VALUES (?, ?, ?, ?, ?, ?)",(dim, "{},{},{}".format(poi["x"], poi["y"],poi["z"]), poi["Text2"], poi["Text3"], code, destination )))
                    #conn.commit()
                    #conn.close()
                except:
                    poi["icon"] = "icons/skyblue/airport.png"
                    return poi2text(poi)
            
                
            

        if poi["Text1"] in lines.keys():
            # print(poi)
            poi["icon"] = lines[poi["Text1"]]
            if poi["Text4"]:
                for polyid in poi["Text4"].split(','):
                    try:
                        intid = int(polyid)
                    except:
                        return poi2text(poi) 
                
                    #conn = sqlite3.connect(dbfile)
                    #cur = conn.cursor()
                    q.put(("INSERT INTO polylines (dim, color, id, coords) VALUES (?, ?, ?, ?)",(dim, poi["Text1"].strip("*"), intid, "{},{},{}".format(poi["x"], poi["y"],poi["z"]))))
                    #conn.commit()
                    #conn.close()

            if poi["Text2"] or poi["Text3"]:  

                return poi2text(poi)


overmarker = [ dict(name="Transpo over", filterFunction=FilterOver, createInfoWindow=True, checked=False)]

nethermarker = [ dict(name="Transpo nether", filterFunction=FilterNether, createInfoWindow=True, checked=False)]

endmarker = [ dict(name="Transpo end", filterFunction=FilterEnd, createInfoWindow=True, checked=False)]

