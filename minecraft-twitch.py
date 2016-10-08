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
import datetime
import dateutil.parser
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
import showandtellraw

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
streaming = False
createTime = ''
title = ""
debug = False

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
    #logging.debug(bookline)
    return bookline


def updateTwitchdata():
    try:
    # Ugly hack to force SSLv3 and avoid
    # urllib2.URLError: <urlopen error [Errno 1] _ssl.c:504: error:14077438:SSL routines:SSL23_GET_SERVER_HELLO:tlsv1 alert internal error>
        import _ssl
        _ssl.PROTOCOL_SSLv23 = _ssl.PROTOCOL_SSLv3
    except:
        pass


    global title        
    global streaming
    global createTime    
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
            logging.debug(streamdata)

        except IOError:
            logging.debug( "IOError, dammit" )
        except ValueError:
            logging.debug( "ValueError, dammit" )

        if streamdata.get("stream") != None:
            updateStreaming(True)
            viewers = int(streamdata.get("stream").get("viewers"))
            createTime = dateutil.parser.parse(streamdata.get("stream").get("created_at"))
            title = streamdata.get("stream").get("channel").get("status")
            logging.debug(title)
            
        elif debug:
            updateStreaming(True)
           
            viewers = 10000
            title = "Barlynaland | Episode 99 - Blah test"
            createTime = dateutil.parser.parse("2016-02-12T04:42:31Z")

        else:
            updateStreaming(False)
            title = "Nope | Nope"
            viewers = 0
            
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

        time.sleep( 60 )

def sendtotwitch( string ):
    global s
    logging.debug( "Sent to twitch: " + string )
    s.send(b"PRIVMSG #greener_ca :" + string.encode("utf-8") + b"\r\n")

def updateStreaming(bool):
    global streaming
    
    if bool == streaming:
        pass
    elif bool == True:
        streaming = True
        vanillabean.send( "/scoreboard teams join Twitch greener_ca" )
        jsontext = showandtellraw.tojson("<aqua^\<><dark_purple^twitch><aqua^\>> you are streaming")
        vanillabean.send("/tellraw greener_ca " + jsontext)
        logging.debug("Started streaming")
    else:
        streaming = False
        vanillabean.send( "/scoreboard teams leave Twitch greener_ca" )
        jsontext = showandtellraw.tojson("<aqua^\<><dark_purple^twitch><aqua^\>> you are NOT  streaming")
        vanillabean.send("/tellraw greener_ca " + jsontext)
        logging.debug("Stopped streaming")
        
def shownewfollowers():
    global newfollowers

    while True:

        for yay in newfollowers:
            logging.debug( "New follower: " + yay )
            sendreset = '/title greener_ca reset'
            finalline1 = '/title greener_ca subtitle {"text":"new follower!","color":"aqua"}'
            finalline2 = '/title greener_ca title {"text":"' + yay + '","color":"green"}'
            vanillabean.send( sendreset )
            vanillabean.send( finalline1)
            vanillabean.send( finalline2)
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

def pretty_date(time=False):
    """
    Get a datetime object or a int() Epoch timestamp and return a
    pretty string like 'an hour ago', 'Yesterday', '3 months ago',
    'just now', etc
    """
    from datetime import datetime
    from datetime import timezone

    now = datetime.now(timezone.utc)
    if type(time) is int:
        diff = now - datetime.fromtimestamp(time)
    elif isinstance(time,datetime):
        diff = now - time
    elif not time:
        diff = now - now
    second_diff = diff.seconds
    day_diff = diff.days
        
    if day_diff < 0:
        return ''
        
    if day_diff == 0:
        if second_diff < 10:
            return "just now"
        if second_diff < 60:
            return str(second_diff) + " seconds ago"
        if second_diff < 120:
            return "a minute ago"
        if second_diff < 3600:
            return str(second_diff // 60) + " minutes ago"
        if second_diff < 7200:
            return "an hour ago"
        if second_diff < 86400:
            return str(second_diff // 3600) + " hours ago"
    if day_diff == 1:
        return "Yesterday"
    if day_diff < 7:
        return str(day_diff) + " days ago"
    if day_diff < 31:
        return str(day_diff // 7) + " weeks ago"
    if day_diff < 365:
        return str(day_diff // 30) + " months ago"
    return str(day_diff // 365) + " years ago"

def startEpisode():
    global title
    showtitle = title.split("|")[0].strip()
    episodetitle = title.split("|")[1].strip()
    for sec in range(300, -1, -1):
        if sec == 10:
            bookcommand = tweetbook()
            logging.debug(bookcommand)
            vanillabean.send(bookcommand)

        timerText = "{} min {} sec".format(*divmod(sec, 60))
        vanillabean.send('/title greener_ca title {{"text": "{}"}}'.format(timerText))
        time.sleep(1)


    time.sleep(8)

    vanillabean.send('/title greener_ca subtitle {{"text": "{1}", "color": "gold"}}\n/title greener_ca title {{"text": "{0}", "color": "gold"}}'.format(showtitle, episodetitle))

    time.sleep(15 * 60)
    
    vanillabean.send('/title greener_ca title {"text": "tweets", "color": "gold"}')
    time.sleep(60 * 4)

    vanillabean.send('/title greener_ca title {"text": "wrap it up", "color": "gold"}')
    
    time.sleep(60)

    vanillabean.send('/title greener_ca subtitle {{"text": "{1}", "color": "gold"}}\n/title greener_ca title {{"text": "{0}", "color": "gold"}}'.format(showtitle, 'see you next time!'))

    time.sleep(11)

    vanillabean.send('/title greener_ca title {{"text": "{}"}}'.format("done"))


def minecraftlistener():
    episodeThread = threading.Thread(target=startEpisode,name="startEpisode")
    episodeThread.setDaemon(True)
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
                logging.debug((event, data))

            '''
            if event == "logged":
                player = data[1]
                if player == "greener_ca":
                    if not episodeThread.is_alive():
                        episodeThread.start()
            '''

                    
            """                if message == "tweets":
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
            """

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



def chatUpdate():
    global streaming
    global debug
    global createTime
    
    while True:
        time.sleep(5 * 60)
        if streaming or debug:
            logging.debug("Updating chat")

            text = "<aqua^\<><dark_purple^twitch><aqua^\>> {}\/{} started {}".format(viewers, len(followers), pretty_date(time=createTime))
            logging.debug(text)
            vanillabean.send("/tellraw greener_ca " + showandtellraw.tojson(text))


def main():


    thread1 = threading.Thread(target=updateTwitchdata,name="updateTwitchdata")
    #thread2 = threading.Thread(target=twitchlistener,name="twitchlistener")
    thread3 = threading.Thread(target=shownewfollowers,name="shownewfollowers")
    # thread4 = threading.Thread(target=minecraftlistener,name="minecraftlistener")
    thread5 = threading.Thread(target=chatUpdate,name="chatUpdate")
    
    thread1.setDaemon(True)
    #thread2.setDaemon(True)
    thread3.setDaemon(True)
    # thread4.setDaemon(True)
    thread5.setDaemon(True)


    
    thread1.start()
    #thread2.start()
    thread3.start()
    # thread4.start()
    thread5.start()

    minecraftlistener()


if __name__ == "__main__":
    main()
