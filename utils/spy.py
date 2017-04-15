#!/usr/bin/python3

import sqlite3
import argparse
import yaml
import json

with open('/minecraft/host/config/server.yaml', 'r') as configfile:
    config = yaml.load(configfile)

dbfile = config['dbfile']




def inSphere(x, y, z, cx, cy, cz, r):
    if x or y or z:
        return (x - cx) ** 2 + (y - cy) ** 2 + (z - cz) ** 2 < r ** 2

def inItems(inv, item):
    return [x for x in json.loads(inv) if item in x]
        

def chestQuery(args):
    con = sqlite3.connect(dbfile)
    con.create_function("inSphere", 7, inSphere)
    
    cur = con.cursor()

    query = 'SELECT datetimestart, datetimeend, dim, x, y, z, diff FROM chestactivity '
    values = ()
    wheres = []

    if args.area:
        wheres.append('inSphere(x, y, z, ?, ?, ?, ?)')
        values += tuple(args.area)

    if args.timeframe:
        wheres.append('((datetimestart BETWEEN ? AND ?) OR (datetimeend BETWEEN ? AND ?))')
        values += tuple(args.timeframe + args.timeframe)



    if args.dim:
        wheres.append('dim == ?')
        values += tuple(args.dim)

    added = removed = False
    if args.action:

        if "added" in args.action:
            added = True

        elif "removed" in args.action:
            removed = True



    if wheres:
        query += "WHERE "


    finalQuery = query + " AND ".join(wheres) + " ORDER BY datetimestart"
    print(finalQuery)
    print(values)
    cur.execute(finalQuery, values)
    results = cur.fetchall()

    for each in results:
        if added:
            each = each[0:6] + (json.loads(each[6])[1],)
        elif removed:
            each = each[0:6] + (json.loads(each[6])[0],)
  
        print(each[0:6])
        items = json.loads(each[6])
        print("  ===Added===")
        for item in items[1]:
            print("  {}".format(item))
        print("  ===Removed===")
        for item in items[0]:
            print("  {}".format(item))


def playerQuery(args):
    con = sqlite3.connect(dbfile)
    con.create_function("inSphere", 7, inSphere)

    cur = con.cursor()

    query = 'SELECT datetime, name, dim, x, y, z, invadded, invremoved, stats FROM playeractivity NATURAL JOIN playerUUID '
    values = ()
    wheres = []

    dimDict = {"n": -1, "o": 0, "e": 1}
    
    if args.action:
        cols = ""
        if "added" in args.action:
            wheres.append("invadded != '[]'")
            cols += "invadded, "
        elif "removed":
            wheres.append("invremoved != '[]'")
            cols += "invremoved, "
    else:
        cols = "invadded, invremoved, "

    query = 'SELECT datetime, name, dim, x, y, z, {}stats FROM playeractivity NATURAL JOIN playerUUID '.format(cols)
            
    if args.dim:
        wheres.append('dim == ?')
        values += (dimDict[args.dim[0]],)
        
    if args.area:
        wheres.append('inSphere(x, y, z, ?, ?, ?, ?)')
        values += tuple(args.area)

    if args.ign:
        wheres.append("({})".format(" OR ".join(len(args.players) * ["name = ?"])))
        values += tuple(args.players)

    if args.timeframe:
        wheres.append('datetime BETWEEN ? AND ?')
        values += tuple(args.timeframe)

    if args.items:
        wheres.append('inItems(invadded, ?)')
        values += tuple(args.items)

    if wheres:
        query += "WHERE "

    finalQuery = query + " AND ".join(wheres) + " ORDER BY datetime"
    print(finalQuery)
    print(values)
    cur.execute(finalQuery, values)
    results = cur.fetchall()

    for each in results:
        print(each[0:6])
        print("  ===Added===")
        for added in json.loads(each[6]):
            print("  {}".format(added))
        print("  ===Removed===")
        for removed in json.loads(each[7]):
            print("  {}".format(removed))
        print("  ==Stats===")
        for stats in json.loads(each[8]).items():
            print("  {}".format(stats))
        


def main():



    parser = argparse.ArgumentParser("This does stuff")
    
    subparsers = parser.add_subparsers(help='sub-command help')

    parser.add_argument('--timeframe', nargs=2)
    parser.add_argument('--area', nargs=4, type=int, help='filter by center x, y, z and r of a sphere')
    parser.add_argument('--dim', nargs=1, help="o=overworld, n=nether, e=end")
        
    chestParser =  subparsers.add_parser("chests", help="")
    playerParser =  subparsers.add_parser("players", help="")


    playerParser.add_argument('--ign', nargs='*')
    playerParser.add_argument('--items', nargs='*')
    playerParser.add_argument('--action', nargs='*')
    playerParser.set_defaults(func=playerQuery)
    
    chestParser.add_argument('--items')
    chestParser.add_argument('--action')
    chestParser.set_defaults(func=chestQuery)
    
    args = parser.parse_args()
    args.func(args)

main()
