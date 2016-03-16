#!/usr/bin/python -u
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
import urllib
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



def daily():
    conn = sqlite3.connect(dbfile)
    cur = conn.cursor()
    cur.execute('select count(datetime) as total, name from activity where datetime >= datetime("now", "-7 days") group by name order by total desc limit 1')
    top = cur.fetchall()[0]
    
    conn.commit()
    conn.close()  
    vanillabean.tweet("Congrats to " + top[1] + " for playing " + str(top[0]) + " minutes this week!")

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

def lag(match):
    ts = match.groups()[0]
    ms = match.groups()[1]
    tick = match.groups()[2]

    conn = sqlite3.connect(dbfile)
    cur = conn.cursor()

    cur.execute("INSERT INTO loglag VALUES (?,?)", (datetime.datetime.now(), tick))

    conn.commit()
    conn.close()

def tellcoords( coords ):
    worlddict = { "o" : ["overworld", "0"], "n" : ["nether", "2"], "e" : ["end", "1"] }

    for each in coords:
        print each, each[0], each[1], each[2]

        vanillabean.send("/tellraw @a " + showandtellraw.tojson("<green^" + servername + "> [Map: _" + worlddict[ each[0].lower() ][0] + " " + each[1] + ', ' + each[2] +  "_|http://" + URL + "/map/#/" + each[1] + "/64/" + each[2] + "/-3/" + worlddict[ each[0].lower() ][1]  + "/0]"))


def telllinks( links ):
    for each in links:
        print each
        vanillabean.send("/tellraw @a " + showandtellraw.tojson("<green^" + servername + "> [_Link_|" + each + "]"))




def status( match ):

    name = match.groups()[1]
    message = match.groups()[2]
    print name, message
    conn = sqlite3.connect(dbfile)
    cur = conn.cursor()

    if message.startswith("!"):
        data = message.split(' ')[1]

        if "twitch" in message:
            cur.execute('INSERT OR IGNORE INTO status (twitch, name) VALUES(?, ?)', (data, name))
            cur.execute('UPDATE status SET twitch = ? WHERE name = ?', (data, name))
        if "youtube" in message:
            cur.execute('INSERT OR IGNORE INTO status (youtube, name) VALUES(?, ?)', (data, name))
            cur.execute('UPDATE status SET youtube = ? WHERE name = ?', (data, name))
        if "twitter" in message:
            cur.execute('INSERT OR IGNORE INTO status (twitter, name) VALUES(?, ?)', (data, name))
            cur.execute('UPDATE status SET twitter = ? WHERE name = ?', (data, name))
        if "reddit" in message:
            cur.execute('INSERT OR IGNORE INTO status (reddit, name) VALUES(?, ?)', (data, name))
            cur.execute('UPDATE status SET reddit = ? WHERE name = ?', (data, name))
        if "clear" in message:
            pass
    else:
        cur.execute('INSERT OR IGNORE INTO status (status, name) VALUES(?, ?)', (message, name))
        cur.execute('UPDATE status SET status = ? WHERE name = ?', (message, name))

    conn.commit()
    conn.close()


def joins(match):
    parsed = match.groups()
    # print match.groups()
    name = parsed[0]
    # print name
    ip = parsed[1].split(':')[0]
    message = "joined"
    
    #tweetmessage = urllib.urlencode({"status": name + " " + message})
    #response = json.loads(oauth_req( "https://api.twitter.com/1.1/statuses/update.json?" + tweetmessage, AccessToken, AccessTokenSecret, http_method="POST"))
    #print response
    
    if message == "joined":
        conn = sqlite3.connect(dbfile)
        cur = conn.cursor()
        try:
            for each in open( otherdata + "/motd.txt", "r" ).readlines():

                time.sleep(1)
                message = u"/tellraw " + name + " " + showandtellraw.tojson( each.strip() )
                vanillabean.send( message )
        except:
            pass
        cur.execute("SELECT * FROM maildrop WHERE slots > 0 and name = ? COLLATE NOCASE", (name,))
        maildrop = cur.fetchall()

        for mail in maildrop:
            coords, name, notify, slots, hidden, ts = mail
            dim, x, y, z = coords.split(",")

            if dim == "e":
                worldnum = "1"
            elif dim == "n":
                worldnum = "2"
            elif dim == "o":
                worldnum = "0"

            toserver = '/tellraw ' + name + ' ' + showandtellraw.tojson('<green^Maildrop> for you at ' + dim + ' [_' + x + ', ' + y + ', ' + z + '_|http://' + URL + '/map/#/' + x + '/' + y + '/' + z + '/-1/' + worldnum + '/0]' )
            vanillabean.send( toserver )

        cur.execute('insert into joins values (?,?,?,?)', (datetime.datetime.now(), name, UUID.get(name, "Unknown"), ip))
        conn.commit()
        conn.close()


def chat(match):
    coordscomma = re.findall("^([OENoen]) (-?\d+), (-?\d+)", match.groups()[1])
    links = re.findall(ur'https?://\S+', match.groups()[1])
    if coordscomma:
        print match.groups()[1]
        print coordscomma

        tellcoords( coordscomma )
    if links:
        print links
        telllinks( links )


def setUUID(match):
    global UUID
    UUID = {match.groups()[0]: match.groups()[1]}
    print UUID


def leaves(match):
    name = match.groups()[0]
    headers = {"user_credentials" : boxcarkey,
    "notification[title]": name + " " + "left",
    "notification[source_name]" : "Barlynaland" }
    url= "https://new.boxcar.io/api/notifications"

    r = requests.post(url, params=headers)


def ip(match):
    parsed = ematch.groups()
    print line
    print match.groups()
    name = parsed[0]
    ip = parsed[1].split(':')[0]
    try:
        hostaddr = socket.gethostbyaddr( ip )[0]
    except:
        hostaddr = "none"

    ipinfo = getgeo( ip )
    ipstat= " ".join( [ip, hostaddr, ipinfo["countryCode"], ipinfo["regionName"], ipinfo["city"], ipinfo["as"] ] )
    print ipstat
    headers = {"user_credentials" : boxcarkey,
    "notification[title]": name + " " + "!!DENIED!!!" + " " + ipstat,
    "notification[source_name]" : "Barlynaland" }
    url= "https://new.boxcar.io/api/notifications"

    r = requests.post(url, params=headers)


def playerlist(numplayers, listofplayers):

    players = listofplayers.split(":")[3].split(",")
    
    print numplayers, players

    # response = vanillabean.send("/tp @a ~ ~ ~")
    # teleplayers = [(each.split()) for each in response.split("Teleported")]
    # print teleplayers
    # teleplayers = [(each[0], each[2].strip(','), each[3].strip(','), each[4]) for each in teleplayers if len(each) > 0]
    # print teleplayers
    conn = sqlite3.connect(dbfile)
    cur = conn.cursor()

    if int(numplayers) > 0:
        for player in players:
            cur.execute('INSERT INTO activity (datetime, name) VALUES (?,?)', (datetime.datetime.now(), player.strip()))

    # for location in teleplayers:
    #     cur.execute('INSERT INTO location (name, x, y, z) VALUES(?,?,?,?)', location)

    conn.commit()
    conn.close()


def acheivements(match):

    name = match.groups()[1]
    ach = match.groups()[2]

    conn = sqlite3.connect(dbfile)
    cur = conn.cursor()

    cur.execute("INSERT INTO achievements VALUES (?,?,?)", (datetime.datetime.now(), name, ach))

    conn.commit()
    conn.close()
    


def minecraftlistener():
    nextlineforlist = False
    numplayers = 0
    logfile = os.path.abspath(mcfolder + "/logs/latest.log")
    f = open(logfile, "r")
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
            UUIDparsematch = re.match("^\[.*\] \[User Authenticator #.*/INFO\]: UUID of player (.*) is (.*)$", line)
            joinparsematch = re.match( "^\[.*\] \[Server thread/INFO\]: (.*)\[/(.*)\] logged in.*$", line )
            leaveparsematch = re.match( "^\[.*\] \[Server thread/INFO\]: ([\w ]*) left the game$", line )
            chatlisten =  re.match("\[.*\] \[Server thread/INFO\]: \<(.*)\> (.*)", line )
            playerlistparsematch = re.match( "^\[(.*)\] \[Server thread/INFO]: There are (.*)/(.*) players online:$", line )
            statusparsematch = re.match( "^\[(.*)\] \[Server thread/INFO\]: <(\w*)> \*\*\*(.*)$", line )
            ipparsematch = re.match( "^\[.*\] \[Server thread/INFO\]: Disc.*name=(.*),pro.*\(/(.*)\).*$", line )
            achievementmatch = re.match("^\[(.*)\] \[Server thread/INFO\]: " + "(\w*) has just earned the achievement \[(.*)\]$", line)
            lagmatch = re.match( "^\[(.*)\] \[Server thread/WARN\]: Can't keep up! Did the system time change, or is the server overloaded\? Running (\d*)ms behind, skipping (\d*) tick\(s\)$", line )

            
            if nextlineforlist:
               
                nextlineforlist = False    
                playerlist(numplayers, line)

            if playerlistparsematch:
                numplayers = playerlistparsematch.groups()[1]
                nextlineforlist = True

            if achievementmatch:
                acheivements(achievementmatch)

            if statusparsematch:
                status(statusparsematch)

            if UUIDparsematch:
                setUUID(UUIDparsematch)

            if chatlisten:
                chat(chatlisten)

#           if leaveparsematch:

#            if ipparsematch:

            if joinparsematch:
                joins( joinparsematch )

            if lagmatch:
                lag(lagmatch)




minecraftlistener()
