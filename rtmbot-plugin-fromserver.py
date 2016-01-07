#!/usr/bin/python -u

import threading
import stat
import socket
import os
import time
import json
import yaml
import requests
import re
import subprocess
import codecs
import sqlite3
#import showandtellraw

crontable = []
crontable.append( [300, "getusers"])
outputs = []
members = {}

with open('/minecraft/host/config/server.yaml', 'r') as configfile:
    config = yaml.load(configfile)


dbfile = config['dbfile']
mcfolder = config['mcdata']
URL = config['URL']
slackchan = config['slackchan']



FREEGEOPIP_URL = 'http://ip-api.com/json/'
#
#SAMPLE_RESPONSE = """
#{
#  "status": "success",
#  "country": "United States",
#  "countryCode": "US",
#  "region": "CA",
#  "regionName": "California",
#  "city": "San Francisco",
#  "zip": "94105",
#  "lat": "37.7898",
#  "lon": "-122.3942",
#  "timezone": "America\/Los_Angeles",
#  "isp": "Wikimedia Foundation",
#  "org": "Wikimedia Foundation",
#  "as": "AS14907 Wikimedia US network",
#  "query": "208.80.152.201"
#}
#"""

def getusers():
    global members

    conn = sqlite3.connect(dbfile)
    cur = conn.cursor()

    cur .execute("SELECT * FROM slackusers")
    members.update({unicode(user[1]): unicode(user[0]) for user in cur.fetchall()})
    # print members

    conn.commit()
    conn.close()


def getgeo(ip):
    url = '{}/{}'.format(FREEGEOPIP_URL, ip)

    response = requests.get(url)
    response.raise_for_status()
    print response
    return response.json()


def coordsmessage( coords ):
    worlddict = { "o" : ["overworld", "0"], "n" : ["nether", "2"], "e" : ["end", "1"] }
    message =[]
    for each in coords:
        print each, each[0], each[1], each[2]

        message.append( ">Map: " + worlddict[ each[0].lower() ][0] + " " + each[1] + ', ' + each[2] + "\n>http://" + URL + "/map/#/" + each[1] + "/64/" + each[2] + "/-3/" + worlddict[ each[0].lower() ][1]  + "/0" )

    return " ".join( message )



def shellquotes( string ):
    return "'" + string.replace("'", "'\\''") + "'"



def minecraftlistener():
    global members
    lastplayer = "Dinnerbone"
    logfile = os.path.abspath(mcfolder + "/logs/latest.log")
    f = codecs.open(logfile,"r", "utf-8")
    file_len = os.stat(logfile)[stat.ST_SIZE]
    f.seek(file_len)
    pos = f.tell()

    getnextline = False
    while True:
        pos = f.tell()
        line = f.readline().strip()
        if not line:
            if os.stat(logfile)[stat.ST_SIZE] < pos:
                f.close()
                time.sleep( 5 )
                f = codecs.open(logfile, "r","utf-8")
                pos = f.tell()
		restartdone = False
            else:
                time.sleep( 1 )
                f.seek(pos)
	else:
            joinparsematch = re.match( "^\[.*\] \[Server thread/INFO\]: (.*)\[/(.*)\] logged in.*$", line )
            infoparsematch = re.match( "^\[.*\] \[Server thread/INFO\]: ([\w]*) (.*)$", line )
            chatlisten =  re.match("\[.*\] \[Server thread/INFO\]: \<(\w*)\> (.*)", line )
            playerlistparsematch = re.match( "^\[(.*)\] \[Server thread/INFO]: There are (.*)/(.*) players online:$", line )
            statusparsematch = re.match( "^\[(.*)\] \[Server thread/INFO\]: <(\w*)> \*\*\*(.*)$", line )
            ipparsematch = re.match( "^\[.*\] \[Server thread/INFO\]: Disc.*name=(.*),pro.*\(/(.*)\).*$", line )

            if chatlisten:
                coordscomma =  re.findall( "^([EONeon]) (-?\d+), (-?\d+)", chatlisten.groups()[1])

                player = unicode(chatlisten.groups()[0])
                player = player.strip(u"\u00a75").strip(u"\u00a7r")
                message = unicode(chatlisten.groups()[1])

                for each in re.findall("@\S+", message):
                    print members
                    print each.rstrip("@")
                    print members.get(each.lstrip("@"))
                    message = message.replace( each, "<@" + members.get(each.lstrip("@"), "*not on slack*") + ">")

            ##    if player == lastplayer and not time.time() >= lasttime + 60:
           #         finalmessage = message
              #  else:
                finalmessage = u"*<" + player +">* " + message
                lastplayer = player
                lasttime = time.time()


                print repr(finalmessage)
                outputs.append( [slackchan, finalmessage.encode('utf-8')  ] )

                if coordscomma:
#                    print chatlisten.groups()[1]
#                    print coordscomma
#
                    outputs.append( [slackchan, coordsmessage( coordscomma ) ] )

            if infoparsematch:
		player = infoparsematch.groups()[0]
		keyword = infoparsematch.groups()[1].split()[0]
		message = infoparsematch.groups()[1]
		if keyword == "left":
			outputs.append( [slackchan, ">*<" + player + ">* left the server"  ] )
		elif keyword == "joined":
			pass
		elif keyword == "lost":
			pass
		elif "whie-listed" in message:
			pass
		elif "players online" in message:
			pass
		elif keyword = "Starting":
			serverrestart = True
		elif keyword = "Done":
			serverrestart = False
		elif not serverrestart:
			outputs.append( [slackchan, ">*<" + player + ">* " + message] )

            if ipparsematch:
                parsed = ipparsematch.groups()
                # print ipparsematch.groups()
                name = parsed[0]
                ip = parsed[1].split(':')[0]
                try:
                    hostaddr = socket.gethostbyaddr( ip )[0]
                except:
                    hostaddr = "none"

                ipinfo = getgeo( ip )
                ipstat= u" ".join( [ip, hostaddr, ipinfo["countryCode"], unicode(ipinfo["regionName"]), unicode(ipinfo["city"]), unicode(ipinfo["as"]) ] )
                print repr(ipstat)
                outputs.append(["G085QQDAA", ">`" + name + "` !!!DENIED!!! " + ipstat])
#                print ipstat
#                headers = {"user_credentials" : boxcarkey,
#                "notification[title]": name + " " + "!!DENIED!!!" + " " + ipstat,
#                "notification[source_name]" : "Barlynaland" }
#                url= "https://new.boxcar.io/api/notifications"
#
#                r = requests.post(url, params=headers)
#
            if joinparsematch:
#
                parsed = joinparsematch.groups()
#                print line
#                print joinparsematch.groups()
                player = parsed[0]
                outputs.append( [slackchan, ">*<" + player + ">*  joined the server"  ] )

                ip = parsed[1].split(':')[0]
                message = "joined"
                try:
                    hostaddr = socket.gethostbyaddr( ip )[0]
                except:
                    hostaddr = "none"
                ipinfo = getgeo( ip )
                ipstat= u" ".join( [ip, hostaddr, ipinfo["countryCode"], unicode(ipinfo["regionName"]), unicode(ipinfo["city"]), unicode(ipinfo["as"]) ] )
                print repr(ipstat)
                outputs.append(["G085QQDAA", "`" + player + "` " + ipstat])



getusers()

thread1 = threading.Thread(target=minecraftlistener,name="minecraftlistener")

thread1.setDaemon(True)

thread1.start()

