#!/usr/bin/python
#coding: utf-8
'''
try:
    # Ugly hack to force SSLv3 and avoid
    # urllib2.URLError: <urlopen error [Errno 1] _ssl.c:504: error:14077438:SSL routines:SSL23_GET_SERVER_HELLO:tlsv1 alert internal error>
    import _ssl
    _ssl.PROTOCOL_SSLv23 = _ssl.PROTOCOL_SSLv3
except:
    pass
'''
import stat
import logging
import threading
import time
import sys
import os
import subprocess
import re
import requests
import json
import socket
import html.parser
import string
import yaml
import oauth2 as oauth
sys.path.append('/minecraft')
import vanillabean


with open('/minecraft/host/config/server.yaml', 'r') as configfile:
    config = yaml.load(configfile)


mcfolder = config['mcdata']
ConsumerKey = config['ConsumerKey']
ConsumerSecret = config['ConsumerSecret']
AccessToken = config['AccessToken']
AccessTokenSecret = config['AccessTokenSecret']
twitchircpass = config['twitchircpass']
twitchname = config['twitchname']
minecraftname = config['minecraftname']
twitter = config['twitter']

followers = {}
newfollowers = []
viewers = 0



s=socket.socket( )

logging.basicConfig(level=logging.DEBUG,
                    format='[%(levelname)s] (%(threadName)-20s) %(message)s',
                    )

def oauth_req( url, key, secret, http_method="GET", post_body="".encode("utf-8"), http_headers=None ):
    consumer = oauth.Consumer( key=ConsumerKey , secret=ConsumerSecret )
    token = oauth.Token( key=key, secret=secret )
    client = oauth.Client( consumer, token )
    (resp,content) = client.request( url, method=http_method, body=post_body, headers=http_headers )
    return content

def tweetbook():
    logging.debug( "Making a tweetbook" )
    h = html.parser.HTMLParser()
    result = oauth_req( "https://api.twitter.com/1.1/favorites/list.json?count=10&screen_name=" + twitter, AccessToken, AccessTokenSecret )
    favs = json.loads(result.decode('utf-8'))
#    print favs
    tweets = []
    for fav in favs:
        # print(repr(fav))
        tweettext = h.unescape(fav.get("text")).replace("\n", r'\n')
        tweettext = tweettext.replace(r'"', r'\\\"')
        tweets.append( r'"[\"\",{\"text\":\"' + tweettext + r'\n\n\",\"color\":\"blue\"},{\"text\":\"' + "- @" + fav.get("user").get("screen_name") + r'\",\"color\":\"dark_aqua\"}]"')

    bookline = r'/give greener_ca minecraft:written_book 1 0 {title:"Tweets",author:"The Internet",pages:[' + ",".join(tweets) + ']}'
    print(bookline)
    return bookline

class LogTail:
    def __init__(self, logfile):
        self.logfile = os.path.abspath(logfile)
        self.f = open(self.logfile,"r")
        file_len = os.stat(self.logfile)[stat.ST_SIZE]
        self.f.seek(file_len)
        self.pos = self.f.tell()
    def _reset(self):
        self.f.close()
        self.f = open(self.logfile, "r")
        self.pos = self.f.tell()
    def tail(self):
        while 1:
            self.pos = self.f.tell()
            line = self.f.readline()
            if not line:
                if os.stat(self.logfile)[stat.ST_SIZE] < self.pos:
                    self._reset()
                else:
                    time.sleep(1)
                    self.f.seek(self.pos)
            else:
                print(line)


def updatefollowers():
    try:
    # Ugly hack to force SSLv3 and avoid
    # urllib2.URLError: <urlopen error [Errno 1] _ssl.c:504: error:14077438:SSL routines:SSL23_GET_SERVER_HELLO:tlsv1 alert internal error>
        import _ssl
        _ssl.PROTOCOL_SSLv23 = _ssl.PROTOCOL_SSLv3
    except:
        pass



    global followers
    global newfollowers
    global viewers
    firstrun = True
    while True:
        # logging.debug( "Updating followers" )
        updatedfollowers = {}
        try:
            streamdata = requests.get("https://api.twitch.tv/kraken/streams/greener_ca").json()
            followerdata = requests.get("https://api.twitch.tv/kraken/channels/greener_ca/follows/?limit=100").json()
        except IOError:
            logging.debug( "IOError, dammit" )
        except ValueError:
            logging.debug( "ValueError, dammit" )

        if streamdata.get("stream") == None:
            viewers = 0
        else:
            viewers = int(streamdata.get("stream").get("viewers"))

        for follows in followerdata.get("follows"):
            updatedfollowers.update( {follows.get("user").get("name") : follows.get("user").get("bio") } )
        if firstrun:
             logging.debug( "First run, not comparing to the any new list" )
             firstrun = False
        else:
             newfollowers += set(updatedfollowers.keys()) - set(followers.keys())
             if len(newfollowers) > 0:
                logging.debug( "Here are your new followers: " + str(newfollowers) )
        followers = updatedfollowers
        logging.debug( "You have " + str(len(followers)) + " followers" )
        vanillabean.send("/scoreboard players set §6Followers §5Twitch " + str(len(followers)))
        vanillabean.send("/scoreboard players set §6Viewers §5Twitch " + str(viewers))

        time.sleep( 60 )

def sendtotwitch( string ):
    global s
    logging.debug( "Sent to twitch: " + string )
    s.send(b"PRIVMSG #greener_ca :" + string.encode("utf-8") + b"\r\n")

def shownewfollowers():
    global newfollowers

    while True:

        for yay in newfollowers:
            logging.debug( "New follower: " + yay )
            sendreset = '/title greener_ca reset'
            finalline1 = '/title greener_ca subtitle {"text":"new follower!","color":"aqua"}'
            finalline2 = '/title greener_ca title {"text":"' + yay + '","color":"green"}'
            vanillabean.send( sendreset )
            vanillabean.send( finalline1, "7")
            vanillabean.send( finalline2, "7")
            systemmessage( [ time.asctime(),  yay, "is a new follower!" ] )
            newfollowers.remove( yay )
            time.sleep( 10 )

        time.sleep( 5 )


def publicmessage( groups ):
    time = groups[0]
    name = groups[1]
    message = groups[2]
    command = message.split()[0]

    name = name.strip(" ").strip("@")

    if command == "!makeitrain":
        finalline = "/toggledownfall"
        vanillabean.send( finalline )
    elif command == "!ip":
        sendtotwitch( "The server address is: minecraft.greener.ca" )
    elif command == "!":
        sendtotwitch( "Commands available are: !ip, !xxxxxxxxxx" )
    else:
        finalline  = '/tellraw ' + minecraftname  + ' {"text":"","extra":[' + twitchmessage( time ) + ',' + colorname( name ) + ',{"text":"' + message.replace('"', r'\"') + '","color":"aqua"}]}'
        vanillabean.send( finalline )


def systemmessage( groups ):

    datetime = groups[0]
    name = groups[1]
    message = groups[2]
    finalline = '/tellraw ' + minecraftname + ' {"text":"","extra":[' + twitchmessage( datetime ) + ',' + colorname( name ) + ',{"text":"' + message + '","color":"dark_purple"}]}'


    vanillabean.send( finalline )


def twitchmessage( datetime ):
    return '{"text":"Twitch","color":"dark_purple","hoverEvent":{"action":"show_text","value":{"text":"' + datetime + '","color":"gold"}}}'

def colorname( name ):
    global twitchname
    if name == twitchname:
        return '{"text":" <' + name + '> ","color":"gold"}'
#    continue
    elif name in followers :
        return '{"text":" <' + name + '> ","color":"green","hoverEvent":{"action":"show_text","value":{"text":"' + str(followers.get( name, "None" ) ).strip() + '","color":"gold"}}}'
    else:
        return '{"text":" <' + name + '> ","color":"aqua"}'


def minecraftlistener():
    logfile = os.path.abspath("/minecraft/host/mcdata/logs/latest.log")
    f = open(logfile,"r")
    file_len = os.stat(logfile)[stat.ST_SIZE]
    f.seek(file_len)
    pos = f.tell()

    while True:
        pos = f.tell()
        line = f.readline().strip()
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
            commandparseRE = re.compile( "\[.*\] \[Server thread/INFO\]: \<(.*)\> !(.*)" )
            commandparsematch = commandparseRE.match( line )

            if commandparsematch == None:
                continue
            elif commandparsematch != None:
                parsed = commandparsematch.groups()

                name = parsed[0]
                message = parsed[1]
                if message == "tweets":
                    vanillabean.send( tweetbook() )
                elif message == "stats":
                    vanillabean.send( "/scoreboard teams join Twitch greener_ca" )
                elif message == "nostats":
                    vanillabean.send( "/scoreboard teams leave Twitch greener_ca" )
                elif "episode" in message:
                    subprocess.Popen( "/minecraft/minecraft-episode.sh " + message.split(" ",1)[1], shell=True )

                elif name == "greener_ca":
                    finalline = message

                    sendtotwitch( finalline  )


def twitchlistener():

    HOST="irc.twitch.tv"
    PORT=6667
    NICK="greener_ca"
    IDENT="twitch catch"
    REALNAME="greener_ca"

    def connect():
        logging.debug("Conecting to IRC using " + REALNAME)
        s.connect((HOST, PORT))
        s.send(bytes("PASS {}\r\n".format( twitchircpass),"UTF-8"))
        s.send(bytes("NICK {}\r\n".format( NICK), "UTF-8"))
        s.send(bytes("USER {} {} bla :{}\r\n".format( IDENT, HOST, REALNAME), "UTF-8"))
        s.send(bytes("JOIN {}\r\n".format( "#greener_ca" ), "UTF-8"))


    connect()

    global followers

    while True:
        readbuffer=""
        readbuffer = readbuffer + str(s.recv(1024))

        if len(readbuffer) == 0:
            logging.debug( "Disconnected! -- Reconnecting to IRC")
            connect()

        temp = readbuffer.split( "\n" )
        readbuffer = temp.pop( )

        for line in temp:
            line=line.rstrip( )
            line=line.split(":" )
            fromserver = line[1].split()

            #logging.debug( [fromserver, line] )
            if (line[0]=="PING "):
                logging.debug("IRC - PING!")
                s.send("PONG %s\r\n" % line[1])
            elif fromserver[1] == "PRIVMSG" and fromserver[2] == "#greener_ca":
                name = fromserver[0].split("!")[0]
                message = line[2]
                datetime = time.asctime()
                logging.debug(  [ datetime, name, message] )
                publicmessage( [ datetime, name, message ] )
            elif fromserver[1] == "JOIN" and fromserver[2] == "#greener_ca":
                name = fromserver[0].split("!")[0]
                message = "joined"
                datetime = time.asctime()
                systemmessage( [ datetime, name, message ] )
            elif fromserver[1] == "PART" and fromserver[2] == "#greener_ca":
                name = fromserver[0].split("!")[0]
                message = "left"
                datetime = time.asctime()
                systemmessage( [ datetime, name, message ] )


def main():


    thread1 = threading.Thread(target=updatefollowers,name="updatefollowers")
    thread2 = threading.Thread(target=twitchlistener,name="twitchlistener")
    thread3 = threading.Thread(target=shownewfollowers,name="shownewfollowers")
    thread4 = threading.Thread(target=minecraftlistener,name="minecraftlistener")

    thread1.setDaemon(True)
    thread2.setDaemon(True)
    thread3.setDaemon(True)
    thread4.setDaemon(True)

    thread1.start()
    thread2.start()
    thread3.start()
    thread4.start()

    while True:
        time.sleep( 1 )


if __name__ == "__main__":
    main()
