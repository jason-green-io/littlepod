#!/usr/bin/python3 -u
import asyncio
import yaml
import os
import codecs
import stat
import time
import re
import requests
import sys
sys.path.append('/minecraft/discord.py')
import discord
import vanillabean
import showandtellraw

with open('/minecraft/host/config/server.yaml', 'r') as configfile:
    config = yaml.load(configfile)


dbfile = config['dbfile']
mcfolder = config['mcdata']
URL = config['URL']
servername = config['name']

discordChannel = config["discordChannel"]
discordPrivChannel = config["discordPrivChannel"]
discordUser = config["discordUser"]
discordPass = config["discordPass"]



serverrestart = False

client = discord.Client()



def telllinks( links ):
    for each in links:
        print( each)
        vanillabean.send("/tellraw @a " + showandtellraw.tojson("<green^" + servername + "> [_Link_|" + each + "]"))


def coordsmessage( coords ):
    worlddict = { "o" : ["overworld", "0"], "n" : ["nether", "2"], "e" : ["end", "1"] }
    message =[]
    for each in coords:
        print (each, each[0], each[1], each[2])

        message.append( "Map: " + worlddict[ each[0].lower() ][0] + " " + each[1] + ', ' + each[2] + "\nhttp://" + URL + "/map/#/" + each[1] + "/64/" + each[2] + "/-3/" + worlddict[ each[0].lower() ][1]  + "/0" )

    return " ".join( message )


def tellcoords( coords ):
    worlddict = { "o" : ["overworld", "0"], "n" : ["nether", "2"], "e" : ["end", "1"] }

    for each in coords:
        print (each, each[0], each[1], each[2])

        vanillabean.send("/tellraw @a " + showandtellraw.tojson("<green^" + servername + "> [Map: _" + worlddict[ each[0].lower() ][0] + " " + each[1] + ', ' + each[2] +  "_|http://" + URL + "/map/#/" + each[1] + "/64/" + each[2] + "/-3/" + worlddict[ each[0].lower() ][1]  + "/0]"))





@client.async_event
def on_status(member, old_game, old_status):
    print(old_status)
    print(member.name)
    print(member.status)

@client.async_event
def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return
    channelobject = discord.Object(id=discordChannel)
    privchannelobject = discord.Object(id=discordPrivChannel)
    print(message.channel.id)
    if message.channel.id == discordChannel:
        links = re.findall('(https?://\S+)', message.content)
        coordscomma =  re.findall( "^([EONeon]) (-?\d+), ?(-?\d+)", message.content)
        discordtext =  u'{"text" : "\u2689 ", "color" : "aqua" }'
        finalline = '/tellraw @a {"text" : "", "extra" : [' + discordtext + ',' + '{"color" : "gold", "text" : "' + str(message.author) + ' "}, ' + '{ "text" : "' + message.content + '"}]}'
        vanillabean.send(finalline)

        if coordscomma:
            
            yield from client.send_message(channelobject, coordsmessage( coordscomma ))
            tellcoords(coordscomma)

        if links:
           telllinks( links )

    if message.channel.id == discordPrivChannel:
        yield from client.send_message(privchannelobject, vanillabean.send(message.content))
        

@client.async_event
def on_ready():
    print('Logged in as')
    print((client.user.name))
    print((client.user.id))
    print('------')
    yield from client.send_message(discord.Object(id=discordChannel),"I crashed, but I'm back now.") 

def getgeo(ip):
    FREEGEOPIP_URL = 'http://ip-api.com/json/'
    url = '{}/{}'.format(FREEGEOPIP_URL, ip)

    response = requests.get(url)
    response.raise_for_status()
    print( response)
    return response.json()


@asyncio.coroutine 
def my_background_task():
    yield from client.wait_until_ready()
    channel = discord.Object(id=discordChannel)
    privchannel = discord.Object(id=discordPrivChannel)


    serverrestart = False
    lastplayer = "Dinnerbone"
    logfile = os.path.abspath(mcfolder + "/logs/latest.log")
    f = codecs.open(logfile,"r", "utf-8")
    file_len = os.stat(logfile)[stat.ST_SIZE]
    f.seek(file_len)
    pos = f.tell()

    getnextline = False
    while not client.is_closed:
        pos = f.tell()
        line = f.readline().strip()
        if not line:
            if os.stat(logfile)[stat.ST_SIZE] < pos:
                f.close()
                yield from asyncio.sleep(5) # task runs every 60 seconds
                time.sleep( 5 )
                f = codecs.open(logfile, "r","utf-8")
                pos = f.tell()
            else:
                
                yield from asyncio.sleep(1) # task runs every 60 seconds
                f.seek(pos)
        else:
            chatlisten =  re.match("\[.*\] \[Server thread/INFO\]: \<(\w*)\> (.*)", line )
            joinparsematch = re.match( "^\[.*\] \[Server thread/INFO\]: (.*)\[/(.*)\] logged in.*$", line )
            infoparsematch = re.match( "^\[.*\] \[Server thread/INFO\]: ([\w]*) (.*)$", line )
            playerlistparsematch = re.match( "^\[(.*)\] \[Server thread/INFO]: There are (.*)/(.*) players online:$", line )
            statusparsematch = re.match( "^\[(.*)\] \[Server thread/INFO\]: <(\w*)> \*\*\*(.*)$", line )
            ipparsematch = re.match( "^\[.*\] \[Server thread/INFO\]: Disc.*name=(.*),pro.*\(/(.*)\).*$", line )

            if chatlisten:
                coordscomma =  re.findall( "^([EONeon]) (-?\d+), (-?\d+)", chatlisten.groups()[1])
                links = re.findall('<(https?://\S+)>', chatlisten.groups()[1])

                player = str(chatlisten.groups()[0])
                player = player.replace("\u00a75","").replace("\u00a7r","")
                message = str(chatlisten.groups()[1])

                for each in re.findall("@\S+", message):
                    memberfrommc = each.lstrip("@")
                    print(memberfrommc)
                    member = discord.utils.find(lambda m: m.name == memberfrommc, client.get_all_members())
                    if member:
                        membermention = member.mention
                        message = message.replace( each, membermention)
                    print(message)
            ##    if player == lastplayer and not time.time() >= lasttime + 60:
           #         finalmessage = message
              #  else:
                
                finalmessage = "`<" + player +">` " + message
                
                if links:
                    telllinks( links )


                print(repr(finalmessage))
                yield from client.send_message(channel, finalmessage)

                if coordscomma:
#                    print chatlisten.groups()[1]
#                    print coordscomma
#
                    yield from client.send_message(channel, coordsmessage( coordscomma ))
                    tellcoords(coordscomma)

            if infoparsematch:
                deathwords = ["blew", "burned", "drowned", "experienced", "fell", "got", "hit", "starved", "suffocated", "tried", "walked", "was", "went", "withered"]
                player = infoparsematch.groups()[0]
                keyword = infoparsematch.groups()[1].split()[0]
                message = infoparsematch.groups()[1]
                if keyword == "left":
                    yield from client.send_message(channel, "`" + player + "` left the server")
                elif keyword == "joined":
                    pass
                elif keyword == "lost":
                    pass
                elif keyword in deathwords:
                    yield from client.send_message(channel, "`" + player + "` " + message)

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
                ipstat= " ".join( [ip, hostaddr, ipinfo["countryCode"], str(ipinfo["regionName"]), str(ipinfo["city"]), str(ipinfo["as"]) ] )
                yield from client.send_message(privchannel, "`" + name + "` !!!DENIED!!! " + ipstat)
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
                yield from client.send_message(channel, "`" + player + "`  joined the server")

                ip = parsed[1].split(':')[0]
                message = "joined"
                try:
                    hostaddr = socket.gethostbyaddr( ip )[0]
                except:
                    hostaddr = "none"
                ipinfo = getgeo( ip )
                ipstat= u" ".join( [ip, hostaddr, ipinfo["countryCode"], str(ipinfo["regionName"]), str(ipinfo["city"]), str(ipinfo["as"]) ] )
                # print(repr(ipstat))
                yield from client.send_message(privchannel, "`" + player + "` " + ipstat)

@asyncio.coroutine
def handle_exception():
    try:
        yield from my_background_task()
    except Exception:
        print("Uhoh!")
        sys.exit(1)

loop = asyncio.get_event_loop()

try:
    asyncio.async(handle_exception())
    loop.run_until_complete(client.run(discordUser, discordPass))
except Exception:
    loop.run_until_complete(client.close())
finally:
    loop.close()






