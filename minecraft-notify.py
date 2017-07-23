#!/usr/bin/python3 -u
import string
import queue
import threading
import stat
import os
import time
import random
import datetime
import json
import yaml
import requests
import re
import sqlite3
import sys
import oauth2 as oauth
from collections import Counter
sys.path.append('/minecraft')
import showandtellraw
import vanillabean
import schedule


sys.path.append('/minecraft/host/config')
from twitch_catch_conf import *
import logging

with open('/minecraft/host/config/server.yaml', 'r') as configfile:
    config = yaml.load(configfile)


dbfile = config['dbfile']
mcfolder = config['mcdata']
URL = config['URL']
servername = config['name']
otherdata = config['otherdata']
tweet = config['tweet']

UUID = ""

q = queue.Queue()

serverName = "<blue^\<><green^{}><blue^\>>".format(servername)
worlddict = { "o" : ["overworld", "0"], "n" : ["nether", "2"], "e" : ["end", "1"] }


def writeToDB():
    while True:
        dbQuery(dbfile, 30, q.get())
        q.task_done()

def getStat(stats, stat):
        if stats:
            evalStats = eval(stats)

            if type(evalStats) is dict:
                return evalStats.get(stat, 0)



        

def dbQuery(db, timeout, query):
    conn = sqlite3.connect(db)
    conn.create_function("getStat", 2, getStat)
    results = []
    for x in range(0, timeout):
        try:
            with conn:
                cur = conn.cursor()
                cur.execute(*query)
                logging.warn(query)
                results = cur.fetchall()
        except sqlite3.OperationalError:
            logging.info("Try {} - Locked".format(x))
            time.sleep(random.random())
            pass
        finally:
            break
    else:
        with conn:
            cur = conn.cursor()
            cur.execute(*query)
            logging.info(query)
            results = cur.fetchall()

    return results


def DBWriter(queryArgs):
    conn = sqlite3.connect(dbfile, 30)
    cur = conn.cursor()
    
    fail = True
    while(fail):
        try:
            cur.execute(*queryArgs)
            conn.commit()
            fail = False
        except sqlite3.OperationalError:
            print("Locked")
            time.sleep(random.random())
            fail = True

threadDBWriter = threading.Thread(target=writeToDB)
threadDBWriter.setDaemon(True)
threadDBWriter.start()

donothing = lambda *args: None        

def stats(stat):

    peeps = dbQuery(dbfile, 30, ('select name, group_concat(stats) from playeractivity natural join playerUUID where datetime >= datetime("now", "-7 days") group by UUID',))

    sumPeep = {}

    for peep in peeps:
        stats = "[" + peep[1] + "]"
        statsCount = Counter()
        stats = eval(stats)
        for each in stats:
            statsCount.update(each)
            sumPeep.update({peep[0]: statsCount})
            
    return sorted([(each[0], each[1].get(stat, 0)) for each in sumPeep.items()], key=lambda a: a[1], reverse=True)[0]


def flyStat():
    name, stat = stats("stat.aviateOneCm")
    vanillabean.tweet("Congrats to {} for flying {} kms this week!".format(name, stat / 100 / 1000))

def minecartStat():
    name, stat = stats("stat.minecartOneCm")
    vanillabean.tweet("Congrats to {} for sitting in a minecart for {} m this week!".format(name, stat / 100 ))

def sneakStat():
    name, stat = stats("stat.sneakTime")
    vanillabean.tweet("Congrats to {} for sneaking {} m this week!".format(name, stat / 100 ))

def boatStat():
    name, stat = stats("stat.boatOneCm")
    vanillabean.tweet("Congrats to {} for boating {} m this week!".format(name, stat / 100 ))

    

def playtimeStat():
    

    
    top = dbQuery(dbfile, 30, ('select count(getStat(stats, "stat.playOneMinute")) as total, name from playeractivity natural join playerUUID where datetime >= datetime("now", "-7 days") group by name order by total desc limit 1',))[0]

    
    vanillabean.tweet("Congrats to {} for playing {} minutes this week!".format(top[1], str(top[0])))

def weekly():
    pass

def monthly():
    pass

if tweet:
    schedule.every().monday.at("07:00").do(playtimeStat)
    schedule.every().tuesday.at("07:00").do(donothing)
    schedule.every().wednesday.at("07:00").do(flyStat)
    schedule.every().thursday.at("07:00").do(minecartStat)
    schedule.every().friday.at("07:00").do(boatStat)
    schedule.every().saturday.at("07:00").do(sneakStat)
    schedule.every().sunday.at("07:00").do(donothing)


def oauth_req( url, key, secret, http_method="GET", post_body="", http_headers=None ):
    consumer = oauth.Consumer( key=ConsumerKey , secret=ConsumerSecret )
    token = oauth.Token( key=key, secret=secret )
    client = oauth.Client( consumer, token )
    (resp,content) = client.request( url, method=http_method, body=post_body, headers=http_headers )
    return content

def eventLag(data):
    ts, ms, tick = data


    q.put(("INSERT INTO loglag VALUES (?,?)", (datetime.datetime.now(), tick)))


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
        if "on" in args:
            print("yup")
            vanillabean.send("/scoreboard teams join mute {}".format(name))
            vanillabean.send("/tell {} Muting Discord".format(name))
        elif "off" in args:
            vanillabean.send("/scoreboard teams leave mute {}".format(name))
            vanillabean.send("/tell {} Un-Muting Discord".format(name))
    

    
    if command == "social":    


        network, user = args.split(" ",1)       
        print(network, user)

        if network == "twitch":
            q.put(('INSERT OR IGNORE INTO status (twitch, name) VALUES(?, ?)', (user, name)))
            q.put(('UPDATE status SET twitch = ? WHERE name = ?', (user, name)))
        if network == "youtube":
            q.put(('INSERT OR IGNORE INTO status (youtube, name) VALUES(?, ?)', (user, name)))
            q.put(('UPDATE status SET youtube = ? WHERE name = ?', (user, name)))
        if network == "twitter":
            q.put(('INSERT OR IGNORE INTO status (twitter, name) VALUES(?, ?)', (user, name)))
            q.put(('UPDATE status SET twitter = ? WHERE name = ?', (user, name)))
        if network == "reddit":
            q.put(('INSERT OR IGNORE INTO status (reddit, name) VALUES(?, ?)', (user, name)))
            q.put(('UPDATE status SET reddit = ? WHERE name = ?', (user, name)))
        if network == "clear":
            pass

    if command == "status":
        if args:
            status = args[0]
        else:
            status = ""

        q.put(('INSERT OR IGNORE INTO status (status, name) VALUES(?, ?)', (status, name)))
        q.put(('UPDATE status SET status = ? WHERE name = ?', (status, name)))

    """
    if command == "maildrop":

        def maildropPage(page):
            if page:
                maildrop = dbQuery(dbfile, 30, ("SELECT * FROM maildrop WHERE name = ? COLLATE NOCASE limit ?, ?", (name, (page - 1) * 5, 5)))


            
                vanillabean.send("/tellraw {} ".format(name) + showandtellraw.tojson("{} <yellow^--- {} maildrop(s) - page {} of {} - \(!maildrop \<page\>\) --->".format(serverName, total, page, totalPages)))
                for mail in maildrop
                    dimcoords, boxname, desc, slots, hidden, inverted = mail
                    dim, coords = dimcoords.split(",",1)
                
                    URLcoords = coords.replace(",", "/")           
            
                    toserver = '/tellraw ' + boxname + ' ' + showandtellraw.tojson(serverName + ' {{Maildrop [_{}_|http://{}/map/#/{}/-1/{}/0]~{} {}}} {}'.format(desc if desc else "{} {}".format(worlddict[dim][0], coords), URL, URLcoords, worlddict[dim][1], worlddict[dim][0], coords, "has {} items".format(slots) if slots else "is empty") )
                    vanillabean.send( toserver )
                    print(toserver)

            else:
                pass





        total = dbQuery(dbfile, 30, ('SELECT count(coords) FROM maildrop WHERE name = ? COLLATE NOCASE', (name,)))[0][0]

        
        pageDiv = divmod(total, 5)
        totalPages = pageDiv[0] + bool(pageDiv[1])
        
        if args:
            try:
                page = int(args[0])
                if page <= totalPages:
                    maildropPage(page)
            except:

                pass
        else:
            page = 1
            maildropPage(page)
    

    """




def eventLogged(data):
    print(data)
    name = data[1]
    # print name
    ip = data[2].split(':')[0]
    
    #tweetmessage = urllib.urlencode({"status": name + " " + message})
    #response = json.loads(oauth_req( "https://api.twitter.com/1.1/statuses/update.json?" + tweetmessage, AccessToken, AccessTokenSecret, http_method="POST"))
    #print response

    token = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5))
    
    try:
        for each in open( otherdata + "/motd.txt", "r" ).readlines():

            time.sleep(1)
            message = "/tellraw " + name + " " + showandtellraw.tojson( each.strip().replace("verifykey", token) )
            vanillabean.send( message )
    except:
        pass


    '''
    maildrop = dbQuery(dbfile, 30, ("SELECT * FROM maildrop WHERE inverted = 0 and slots > 0 and name = ? COLLATE NOCASE", (name,)))
    

    maildropinv = dbQuery(dbfile, 30, ("SELECT * FROM maildrop WHERE inverted = 1 and slots = 0 and name = ? COLLATE NOCASE", (name,)))

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
    '''
    q.put(('INSERT INTO joins VALUES (?,?,?,?)', (datetime.datetime.now(), name, UUID.get(name, "Unknown"), ip)))
    q.put(('REPLACE INTO discordverify (name, token) VALUES (?, ?)', (name, token)))
    
   
   


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
  

    if int(numplayers) > 0:
        for player in players:
            q.put(('INSERT INTO activity (datetime, name) VALUES (?,?)', (datetime.datetime.now(), player.strip())))

    # for location in teleplayers:
    #     cur.execute('INSERT INTO location (name, x, y, z) VALUES(?,?,?,?)', location)

  


def eventAchievement(data):

    time, name, ach = data


    q.put(("INSERT INTO achievements VALUES (?,?,?)", (datetime.datetime.now(), name, ach)))
    vanillabean.tweet('{} just got "{}"'.format(name, ach))

    


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
