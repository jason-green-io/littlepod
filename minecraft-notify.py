#!/usr/bin/python -u
import queue
import threading
import stat
import os
import time
import datetime
import json
import yaml
import requests
import re
import sqlite3
import sys
import oauth2 as oauth
sys.path.append('/minecraft')
import showandtellraw
import vanillabean
import schedule

sys.path.append('/minecraft/host/config')
from twitch_catch_conf import *

with open('/minecraft/host/config/server.yaml', 'r') as configfile:
    config = yaml.load(configfile)


dbfile = config['dbfile']
mcfolder = config['mcdata']
URL = config['URL']
servername = config['name']
otherdata = config['otherdata']

UUID = ""

q = queue.Queue()

serverName = "<aqua^\<><green^{}><aqua^\>>".format(servername)
worlddict = { "o" : ["overworld", "0"], "n" : ["nether", "2"], "e" : ["end", "1"] }


def writeToDB():
    while True:
        DBWriter(q.get())
        q.task_done()


def DBWriter(queryArgs):
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
threadDBWriter.start()

        
def daily():
    conn = sqlite3.connect(dbfile)
    cur = conn.cursor()
    cur.execute('select count(datetime) as total, name from activity where datetime >= datetime("now", "-7 days") group by name order by total desc limit 1')
    top = cur.fetchall()[0]
    
    conn.commit()
    conn.close()  
    vanillabean.tweet("Congrats to {} for playing {} minutes this week!".format(top[1], str(top[0])))

def weekly():
    pass

def monthly():
    pass


schedule.every().monday.at("07:00").do(daily)
#schedule.every(5).minutes.do(daily)

def oauth_req( url, key, secret, http_method="GET", post_body="", http_headers=None ):
    consumer = oauth.Consumer( key=ConsumerKey , secret=ConsumerSecret )
    token = oauth.Token( key=key, secret=secret )
    client = oauth.Client( consumer, token )
    (resp,content) = client.request( url, method=http_method, body=post_body, headers=http_headers )
    return content

def eventLag(data):
    ts, ms, tick = data

    conn = sqlite3.connect(dbfile)
    cur = conn.cursor()

    cur.execute("INSERT INTO loglag VALUES (?,?)", (datetime.datetime.now(), tick))

    conn.commit()
    conn.close()

def tellcoords( coords ):
    

    for each in coords:
        print(each, each[0], each[1], each[2])

        vanillabean.send("/tellraw @a " + showandtellraw.tojson(serverName + " [Map: _{} {}_|http://{}/map/#/{}/64/{}/-3/{}/0]".format(worlddict[ each[0].lower() ][0], ", ".join([each[1], each[2]]), URL, each[1], each[2], worlddict[ each[0].lower() ][1])))


def telllinks( links ):
    for each in links:
        print(each)
        vanillabean.send("/tellraw @a " + showandtellraw.tojson(serverName + " [_Link_|{}]".format(each)))


def eventCommand(data):
    time, name, message = data
    command = message.split(" ",1)[0]
    args = message.split(" ",1)[1:]
    print(args)
    name = name.replace("?7","").replace("?r","")
    if command == "mute":
        if args == "on":
            vanillabean.send("/scoreboard teams join mute {}".format(name))
            vanillabean.send("/tell {} Muting Discord".format(name))
        elif args == "off":
            vanillabean.send("/scoreboard teams leave mute {}".format(name))
            vanillabean.send("/tell {} Un-Muting Discord".format(name))
    
    conn = sqlite3.connect(dbfile)
    cur = conn.cursor()
    
    if command == "social":    


        network, user = args.split(" ",1)       
        print(network, user)

        if network == "twitch":
            cur.execute('INSERT OR IGNORE INTO status (twitch, name) VALUES(?, ?)', (user, name))
            cur.execute('UPDATE status SET twitch = ? WHERE name = ?', (user, name))
        if network == "youtube":
            cur.execute('INSERT OR IGNORE INTO status (youtube, name) VALUES(?, ?)', (user, name))
            cur.execute('UPDATE status SET youtube = ? WHERE name = ?', (user, name))
        if network == "twitter":
            cur.execute('INSERT OR IGNORE INTO status (twitter, name) VALUES(?, ?)', (user, name))
            cur.execute('UPDATE status SET twitter = ? WHERE name = ?', (user, name))
        if network == "reddit":
            cur.execute('INSERT OR IGNORE INTO status (reddit, name) VALUES(?, ?)', (user, name))
            cur.execute('UPDATE status SET reddit = ? WHERE name = ?', (user, name))
        if network == "clear":
            pass

    if command == "status":
        if args:
            status = args[0]
        else:
            status = ""

        cur.execute('INSERT OR IGNORE INTO status (status, name) VALUES(?, ?)', (status, name))
        cur.execute('UPDATE status SET status = ? WHERE name = ?', (status, name))


    if command == "maildrop":
            cur.execute("SELECT * FROM maildrop WHERE name = ? COLLATE NOCASE", (name,))
            maildrop = cur.fetchall()

            for mail in maildrop:
                dimcoords, boxname, desc, slots, hidden, inverted = mail
                dim, coords = dimcoords.split(",",1)

                URLcoords = coords.replace(",", "/")           

                toserver = '/tellraw ' + boxname + ' ' + showandtellraw.tojson(serverName + ' {{Maildrop [_{}_|http://{}/map/#/{}/-1/{}/0]~{} {}}} {}'.format(desc if desc else "{} {}".format(worlddict[dim][0], coords), URL, URLcoords, worlddict[dim][1], worlddict[dim][0], coords, "has {} items".format(slots) if slots else "is empty") )
                vanillabean.send( toserver )
                print(toserver)
                
    

    conn.commit()
    conn.close()

    conn.commit()
    conn.close()





def eventLogged(data):
    print(data)
    name = data[1]
    # print name
    ip = data[2].split(':')[0]
    
    #tweetmessage = urllib.urlencode({"status": name + " " + message})
    #response = json.loads(oauth_req( "https://api.twitter.com/1.1/statuses/update.json?" + tweetmessage, AccessToken, AccessTokenSecret, http_method="POST"))
    #print response
    

    try:
        for each in open( otherdata + "/motd.txt", "r" ).readlines():

            time.sleep(1)
            message = "/tellraw " + name + " " + showandtellraw.tojson( each.strip() )
            vanillabean.send( message )
    except:
        pass


    


    conn = sqlite3.connect(dbfile, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
    cur = conn.cursor()

    '''
    cur.execute('select m.name, desc,  m.coords, slots, c.ts as "[timestamp]", a.datetime as "[timestamp]"from maildrop as m natural left join (select coords, chest, ts from chests group by coords order by ts) as c join (select name, datetime from activity where datetime < datetime("now", "-5 minutes") group by name order by datetime) as a on c.ts > a.datetime and a.name == m.name ;')

    results = cur.fetchall()

    conn.commit()
    conn.close()


    attrs = ['years', 'months', 'days', 'hours', 'minutes']
    human_readable = lambda delta: ['%d %s' % (getattr(delta, attr), getattr(delta, attr) > 1 and attr or attr[:-1]) for attr in attrs if getattr(delta, attr)]



    for each in results:
        name, desc, coords, slots, updateTime, playerTime = each
        coordsSplit = coords.split(',')
        maplink = "http://{}/map/#/{}/64/{}/-3/{}/0".format(URL, coordsSplit[1], coordsSplit[2], worlddict[coordsSplit[0]][1])
        print(maplink)
        print("hey {}, [{}|{}] has {} slots filled, updated {} ago".format(each[0], each[1] if each[1] else "On map", maplink, each[3], " ".join(human_readable(relativedelta(datetime.datetime.now(), each[4])))))

    '''






    cur.execute("SELECT * FROM maildrop WHERE inverted = 0 and slots > 0 and name = ? COLLATE NOCASE", (name,))
    maildrop = cur.fetchall()

    cur.execute("SELECT * FROM maildrop WHERE inverted = 1 and slots = 0 and name = ? COLLATE NOCASE", (name,))
    maildropinv = cur.fetchall()

    for mail in maildrop + maildropinv:
        dimcoords, boxname, desc, slots, hidden, inverted = mail
        dim, coords = dimcoords.split(",",1)

        if dim == "e":
            worldnum = "1"
        elif dim == "n":
            worldnum = "2"
        elif dim == "o":
            worldnum = "0"
        
        URLcoords = coords.replace(",", "/")           

        toserver = '/tellraw ' + boxname + ' ' + showandtellraw.tojson(serverName + ' {{Maildrop [_{}_|http://{}/map/#/{}/-1/{}/0]~{} {}}} {}'.format(desc if desc else "{} {}".format(worlddict[dim][0], coords), URL, URLcoords, worldnum, worlddict[dim][0], coords, "has {} items".format(slots) if slots else "is empty") )
        vanillabean.send( toserver )
        print(toserver)
    q.put(('insert into joins values (?,?,?,?)', (datetime.datetime.now(), name, UUID.get(name, "Unknown"), ip)))
    

    conn.commit()
    conn.close()


def eventChat(data):
    coordscomma = re.findall("^([OENoen]) (-?\d+), ?(-?\d+)", data[2])
    links = re.findall(r'https?://\S+', data[2])
    if coordscomma:
        print(coordscomma)
        tellcoords(coordscomma)
    
    if links:
        print(links)
        telllinks(links)


def eventUUID(data):
    global UUID
    UUID = {data[1]: data[2]}
    print(UUID)


def playerlist(numplayers, line):

    players = line.split(":")[3].split(",")
    
    print(numplayers, players)

    # response = vanillabean.send("/tp @a ~ ~ ~")
    # teleplayers = [(each.split()) for each in response.split("Teleported")]
    # print teleplayers
    # teleplayers = [(each[0], each[2].strip(','), each[3].strip(','), each[4]) for each in teleplayers if len(each) > 0]
    # print teleplayers
    conn = sqlite3.connect(dbfile)
    cur = conn.cursor()

    if int(numplayers) > 0:
        for player in players:
            q.put(('INSERT INTO activity (datetime, name) VALUES (?,?)', (datetime.datetime.now(), player.strip())))

    # for location in teleplayers:
    #     cur.execute('INSERT INTO location (name, x, y, z) VALUES(?,?,?,?)', location)

    conn.commit()
    conn.close()


def eventAchievement(data):

    time, name, ach = data

    conn = sqlite3.connect(dbfile)
    cur = conn.cursor()

    cur.execute("INSERT INTO achievements VALUES (?,?,?)", (datetime.datetime.now(), name, ach))
    vanillabean.tweet('{} just got "{}"'.format(name, ach))
    conn.commit()
    conn.close()
    


def minecraftlistener():
    nextlineforlist = False
    numplayers = 0
    logfile = os.path.abspath(mcfolder + "/logs/latest.log")
    f = open(logfile, "r", encoding="utf-8")
    file_len = os.stat(logfile)[stat.ST_SIZE]
    f.seek(file_len)
    pos = f.tell()
    UUID = {}

    while True:
        pos = f.tell()
        line = f.readline().strip()
        schedule.run_pending()
        if not line:
            if os.stat(logfile)[stat.ST_SIZE] < pos:
                f.close()
                time.sleep( 1 )
                f = open(logfile, "r")
                pos = f.tell()
            else:
                time.sleep( 1 )
                f.seek(pos)
        else:
            
            eventData = vanillabean.genEvent(line)
            event = ""
            data = ()
            
            if eventData:
                # print(eventData)
                event, data = eventData
                print(event, data)
            
            if nextlineforlist:
               
                nextlineforlist = False    
                playerlist(numplayers, line)

            if event == "playerList":
                numplayers = data[1]
                nextlineforlist = True

            if event == "achievement":
                eventAchievement(data)

            if event == "command":
                eventCommand(data)

            if event == "UUID":
                eventUUID(data)

            if event == "chat":
                eventChat(data)

            if event == "logged":
                eventLogged(data)

            if event == "lag":
                eventLag(data)




minecraftlistener()
