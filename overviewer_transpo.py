import json
import sqlite3
import yaml
import math

with open('/minecraft/host/config/server.yaml', 'r') as configfile:
    config = yaml.load(configfile)


dbfile = config['dbfile']




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



def polyFilterOver( poi ):
    return polyFilter( poi, "o" ) 


def polyFilterNether( poi ):
    return polyFilter( poi, "n" ) 


def polyFilterEnd( poi):
    return polyFilter( poi, "e" ) 


def polyFilter(poi, dim):
    if poi["id"] == "transpo" and poi["dim"] == dim:
        # print poi
        return poi

# Overworld
def signFilterPurplelineOver( poi ):
    return signFilterpoint(poi, "o", "purpleline")
def signFilterRedlineOver( poi ):
    return signFilterpoint(poi, "o", "redline")
def signFilterBluelineOver( poi ):
    return signFilterpoint(poi, "o", "blueline")
def signFilterYellowlineOver( poi ):
    return signFilterpoint(poi, "o", "yellowline")
def signFilterGreenlineOver( poi ):
    return signFilterpoint(poi, "o", "greenline")
def signFilterFlywayOver( poi ):
    return signFilterfly(poi, "o")


# Nether
def signFilterPurplelineNether( poi ):
    return signFilterpoint(poi, "n", "purpleline")
def signFilterRedlineNether( poi ):
    return signFilterpoint(poi, "n", "redline")
def signFilterBluelineNether( poi ):
    return signFilterpoint(poi, "n", "blueline")
def signFilterYellowlineNether( poi ):
    return signFilterpoint(poi, "n", "yellowline")
def signFilterGreenlineNether( poi ):
    return signFilterpoint(poi, "n", "greenline")
def signFilterFlywayNether( poi ):
    return signFilterfly(poi, "n")

# End
def signFilterPurplelineEnd( poi ):
    return signFilterpoint(poi, "e", "purpleline")
def signFilterRedlineEnd( poi ):
    return signFilterpoint(poi, "e", "redline")
def signFilterBluelineEnd( poi ):
    return signFilterpoint(poi, "e", "blueline")
def signFilterYellowlineEnd( poi ):
    return signFilterpoint(poi, "e", "yellowline")
def signFilterGreenlineEnd( poi ):
    return signFilterpoint(poi, "e", "greenline")
def signFilterFlywayEnd( poi ):
    return signFilterfly(poi, "e")



def signFilterfly(poi, dim, poi2text=poi2text):
    if poi['id'] in ['Sign', "minecraft:sign"] and "*flyway*" in poi['Text1']:
        # print(poi)
        lines = ["Text1","Text2","Text3","Text4"]
        text = []
        for each in lines:
            try:
                poi[each] = json.loads(poi[each]).get("text")

            except:
                pass
            text.append(poi[each].replace(u"\uf701","").replace(u"\uf700",""))
        print(text)
        if text[3]:
            try:
                code, destination = tuple(text[3].split("-"))    
                if len(code) != 3 and len(destination) != 3:
                    return poi2text(poi) 
                conn = sqlite3.connect(dbfile)
                cur = conn.cursor()
                cur.execute("INSERT INTO flyway (dim, coords, text1, text2, code, destination) VALUES (?, ?, ?, ?, ?, ?)",(dim, "{},{},{}".format(poi["x"], poi["y"],poi["z"]), text[1], text[2], code, destination ))
                conn.commit()
                conn.close()
            except:
                return poi2text(poi)
        else:
            return poi2text(poi)   
        #return poi2text(poi)


def signFilterpoint(poi, dim, color, poi2text=poi2text):
    if poi['id'] in ['Sign', "minecraft:sign"] and "*{}*".format(color) in poi['Text1']:
        # print(poi)
        lines = ["Text1","Text2","Text3","Text4"]
        text = []
        for each in lines:
            try:
                poi[each] = json.loads(poi[each]).get("text")

            except:
                pass
            text.append(poi[each].replace(u"\uf701","").replace(u"\uf700",""))

        if text[3]:
            for polyid in text[3].split(','):
                try:
                    intid = int(polyid)
                except:
                    return poi2text(poi) 
                
                conn = sqlite3.connect(dbfile)
                cur = conn.cursor()
                cur.execute("INSERT INTO polylines (dim, color, id, coords) VALUES (?, ?, ?, ?)",(dim, color, intid, "{},{},{}".format(poi["x"], poi["y"],poi["z"])))
                conn.commit()
                conn.close()

        if text[1] or text[2]:  

            return poi2text(poi)






overmarker = [ dict(name="NetherTrans purple over", icon="icons/purple/highway.png", filterFunction=signFilterPurplelineOver, createInfoWindow=True, checked=True),
 dict(name="NetherTrans red over", icon="icons/red/highway.png", filterFunction=signFilterRedlineOver, createInfoWindow=True, checked=True),
 dict(name="NetherTrans blue over", icon="icons/blue/highway.png", filterFunction=signFilterBluelineOver, createInfoWindow=True, checked=True),
 dict(name="NetherTrans green over", icon="icons/green/highway.png", filterFunction=signFilterGreenlineOver, createInfoWindow=True, checked=True),
 dict(name="NetherTrans yellow over", icon="icons/yellow/highway.png", filterFunction=signFilterYellowlineOver, createInfoWindow=True, checked=True),
 dict(name="FlyWay over", icon="icons/skyblue/airport.png", filterFunction=signFilterFlywayOver, createInfoWindow=True, checked=True),
 dict(name="transpo over", icon="", filterFunction=polyFilterOver, createInfoWindow=True, checked=True) ]

nethermarker = [ dict(name="NetherTrans purple nether", icon="icons/purple/highway.png", filterFunction=signFilterPurplelineNether, createInfoWindow=True, checked=True),
 dict(name="NetherTrans red nether", icon="icons/red/highway.png", filterFunction=signFilterRedlineNether, createInfoWindow=True, checked=True),
 dict(name="NetherTrans blue nether", icon="icons/blue/highway.png", filterFunction=signFilterBluelineNether, createInfoWindow=True, checked=True),
 dict(name="NetherTrans green nether", icon="icons/green/highway.png", filterFunction=signFilterGreenlineNether, createInfoWindow=True, checked=True),
 dict(name="NetherTrans yellow nether", icon="icons/yellow/highway.png", filterFunction=signFilterYellowlineNether, createInfoWindow=True, checked=True),
 dict(name="FlyWay nether", icon="icons/skyblue/airport.png", filterFunction=signFilterFlywayNether, createInfoWindow=True, checked=True),
 dict(name="transpo nether", icon="", filterFunction=polyFilterNether, createInfoWindow=True, checked=True) ]

endmarker = [ dict(name="NetherTrans purple end", icon="icons/purple/highway.png", filterFunction=signFilterPurplelineEnd, createInfoWindow=True, checked=True),
 dict(name="NetherTrans red end", icon="icons/red/highway.png", filterFunction=signFilterRedlineEnd, createInfoWindow=True, checked=True),
 dict(name="NetherTrans blue end", icon="icons/blue/highway.png", filterFunction=signFilterBluelineEnd, createInfoWindow=True, checked=True),
 dict(name="NetherTrans green end", icon="icons/green/highway.png", filterFunction=signFilterGreenlineEnd, createInfoWindow=True, checked=True),
 dict(name="NetherTrans yellow end", icon="icons/yellow/highway.png", filterFunction=signFilterYellowlineEnd, createInfoWindow=True, checked=True), 
 dict(name="FlyWay end", icon="icons/skyblue/airport.png", filterFunction=signFilterFlywayEnd, createInfoWindow=True, checked=True), 
 dict(name="transpo end", icon="icons/yellow/highway.png", filterFunction=polyFilterEnd, createInfoWindow=True, checked=True) ]

