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
import discord
sys.path.append('/minecraft/discord.py')
import vanillabean
import showandtellraw

with open('/minecraft/host/config/server.yaml', 'r') as configfile:
    config = yaml.load(configfile)

name = config['name']
dbfile = config['dbfile']
mcfolder = config['mcdata']
URL = config['URL']
servername = config['name']

serverFormat = "<blue^\<><green^{}><blue^\>>"
playerFormat = "<blue^\<><white^{}><blue^\>>"
patronFormat = "<blue^\<><red^{}><blue^\>>"

discordChannel = config["discordChannel"]
discordPrivChannel = config["discordPrivChannel"]
discordToken = config["discordToken"]

if not discordToken:
    print("Discord token not set")
    sys.exit()


channelobject = discord.Object(id=discordChannel)
privchannelobject = discord.Object(id=discordPrivChannel)

serverrestart = False

client = discord.Client()



def telllinks( links ):
    for each in links:
        print( each)
        vanillabean.send("/tellraw @a " + showandtellraw.tojson((serverFormat + " [_Link_|{}]").format(servername, each)))


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

        vanillabean.send("/tellraw @a " + showandtellraw.tojson(serverFormat.format(servername) + "[Map: _" + worlddict[ each[0].lower() ][0] + " " + each[1] + ', ' + each[2] +  "_|http://" + URL + "/map/#/" + each[1] + "/64/" + each[2] + "/-3/" + worlddict[ each[0].lower() ][1]  + "/0]"))





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
    print(message.author.display_name, message.clean_content.encode("utf-8"))

    if message.channel.is_private:
        coordscomma =  re.findall( "^([EONeon]) (-?\d+), ?(-?\d+)", message.content)
        
        if coordscomma:
            
            yield from client.send_message(channelobject, coordsmessage( coordscomma ))
            tellcoords(coordscomma)

    if message.channel.id == discordChannel:
        links = re.findall('(https?://\S+)', message.content)

        display_name = str(message.author.display_name)
        discordName = str(message.author)
        messagetext = str(message.clean_content) 
        messagetext = messagetext.replace('"', r"\"")
        discordtext =  u'{"text" : "\\u2689 ", "color" : "blue" }'

        print([a.name for a in message.author.roles])
        
        if message.author.bot:
            nameFormat = '<blue^\<>{{<green^{}>~{}}}<blue^\>> '
            mcplayer, mcmessage = messagetext.split(" ", 1)
            messagetext = mcplayer.strip('`') + " " + mcmessage
        elif "patron" in [a.name for a in message.author.roles]:
            
            nameFormat = '<blue^\<>{{<red^{}>~{}}}<blue^\>> '
        else:
            nameFormat = '<blue^\<>{{<white^{}>~{}}}<blue^\>> '

        #finalline = '/tellraw @a[team=!mute] {{"text" : "", "extra" : [{}, {{"color" : "gold", "text" : "{} "}}, {{"text" : "{}"}}]}}'.format(discordtext, display_name, messagetext)
        tellrawText =  nameFormat.format(display_name.replace("_", "\_"), discordName.replace("_", "\_").replace("@","\@"))
        finalline = '/tellraw @a[team=!mute] ' + showandtellraw.tojson(tellrawText, noparse=messagetext)

        vanillabean.send(finalline)


        if links:
           telllinks( links )

    if message.channel.id == discordPrivChannel and not message.author.bot:
        yield from client.send_message(privchannelobject, vanillabean.send(message.content))
        

@client.async_event
def on_ready():
    print('Logged in as')
    print((client.user.name))
    print((client.user.id))
    print('------')
    yield from client.send_message(discord.Object(id=discordPrivChannel),"I crashed, but I'm back now.") 

def getgeo(ip):
    FREEGEOPIP_URL = 'http://ip-api.com/json/'
    url = '{}/{}'.format(FREEGEOPIP_URL, ip)

    response = requests.get(url)
    response.raise_for_status()
    print( response)
    return response.json()

@asyncio.coroutine 
def eventIp(data):
    name = data[1]
    ip = data[2].split(':')[0]
    try:
        hostaddr = socket.gethostbyaddr( ip )[0]
    except:
        hostaddr = "none"

    ipinfo = getgeo( ip )
    ipstat = " ".join( [ip, hostaddr, ipinfo["countryCode"], str(ipinfo["regionName"]), str(ipinfo["city"]), str(ipinfo["as"]) ] )
    yield from client.send_message(privchannelobject, "`{}` !!!DENIED!!! {}".format(name, ipstat))


@asyncio.coroutine 
def eventDeath1(data):
    player = data[1]
    player = re.sub(r"\?\d(.*)\?r",r"\1", player)
    message = data[2:]
    yield from client.send_message(channelobject, "`{}` {}".format(player, "".join(message)))

@asyncio.coroutine 
def eventDeath2(data):
    player = data[1]
    player = re.sub(r"\?\d(.*)\?r",r"\1", player)
    message = list(data[2:])
    message[1] = "`{}`".format(message[1])
    yield from client.send_message(channelobject, "`{}` {}".format(player, "".join(message)))


@asyncio.coroutine 
def eventDeath3(data):
    player = data[1]
    player = re.sub(r"\?\d(.*)\?r",r"\1", player)
    message = list(data[2:])
    message[1] = "`{}`".format(message[1])
    message[1] = re.sub(r"\?\d(.*)\?r",r"\1", message[1])
    message[3] = "`{}`".format(message[3])
    yield from client.send_message(channelobject, "`{}` {}".format(player, "".join(message)))


@asyncio.coroutine 
def eventLogged(data):
    player = data[1]
    player = re.sub(r"\?\d(.*)\?r",r"\1", player)
    yield from client.send_message(channelobject, "`{}`  joined the server".format(player))

    ip = data[2].split(':')[0]
    message = "joined"
    try:
        hostaddr = socket.gethostbyaddr( ip )[0]
    except:
        hostaddr = "none"
    ipinfo = getgeo( ip )
    ipstat= u" ".join( [ip, hostaddr, ipinfo["countryCode"], str(ipinfo["regionName"]), str(ipinfo["city"]), str(ipinfo["as"]) ] )
    yield from client.send_message(privchannelobject, "`{}` {}".format(player, ipstat))

@asyncio.coroutine 
def eventLeft(data):
    player = data[1]
    player = re.sub(r"\?\d(.*)\?r",r"\1", player)
    yield from client.send_message(channelobject, "`{}` left the server".format(player))



@asyncio.coroutine 
def eventChat(data):
    coordscomma =  re.findall( "^([EONeon]) (-?\d+), ?(-?\d+)", data[2])
    links = re.findall('<(https?://\S+)>', data[2])

    player = data[1]
    message = data[2]

    for each in re.findall("@\S+", message):
        memberfrommc = each.lstrip("@")
        print(memberfrommc)
        member = discord.utils.find(lambda m: m.name == memberfrommc, client.get_all_members())
        if member:
            membermention = member.mention
            message = message.replace( each, membermention)
        print(message)
    
    
    if links:
        telllinks( links )

    if not player.startswith("?7"):
        player = re.sub(r"\?\d(.*)\?r",r"\1", player)
        finalmessage = "`<{}>` {}".format(player, message)
        print(repr(finalmessage))
        yield from client.send_message(channelobject, finalmessage)

    if coordscomma:
        yield from client.send_message(channelobject, coordsmessage( coordscomma ))
        tellcoords(coordscomma)

@asyncio.coroutine 
def my_background_task():
    yield from client.wait_until_ready()


    serverrestart = False
    logfile = os.path.abspath(mcfolder + "/logs/latest.log")
    f = codecs.open(logfile,"r", "utf-8")
    file_len = os.stat(logfile)[stat.ST_SIZE]
    f.seek(file_len)
    pos = f.tell()

    nextlineformute = False
    mutedlist = []
    nextlineforlist = False
    numplayers = 0

    while not client.is_closed:
        pos = f.tell()
        line = f.readline().strip()
        if not line:
            if os.stat(logfile)[stat.ST_SIZE] < pos:
                f.close()
                yield from asyncio.sleep(5)
                time.sleep( 5 )
                f = codecs.open(logfile, "r","utf-8")
                pos = f.tell()
            else:
                
                yield from asyncio.sleep(1)
                f.seek(pos)
        else:
            eventData = vanillabean.genEvent(line)
            event = ""
            data = ()
            
            if eventData:
                # print(eventData)
                event, data = eventData
                print(event, data)
            
            if nextlineformute:
                nextlineformute = False
                mutedlist = [a.strip(",") for a in line.split(":")[3].split(" ")]
                mutedlist.remove('')
            
            if nextlineforlist:
                nextlineforlist = False    
                players = [a.strip() for a in line.split(":")[3].split(",")]
                formattedplayers = ["~{}".format(a) if a in mutedlist else a for a in players]
                currentTopic = client.get_channel(discordChannel).topic
                topicLineList = currentTopic.split('\n')
                topicLine = [line for line in enumerate(topicLineList) if line[1].startswith(name)][0][0]
                
                topicLineList[topicLine] = "{} - {}/20 - `({})`".format(name, numplayers, " ".join(formattedplayers))
                
                yield from client.edit_channel(client.get_channel(discordChannel), position=1, name="whitelisted-servers", topic="\n".join(topicLineList))
           
            if event == "muteTeam":
                nummuteplayers = data[1]
                nextlineformute = True 

            if event == "playerList":
                numplayers = data[1]
                nextlineforlist = True
            
            if event == "chat":
                yield from eventChat(data)

            if event == "logged":
                yield from eventLogged(data)

            if event == "ip":
                yield from eventIp(data)

            if event.startswith("deathWeapon"):
                yield from eventDeath3(data)

            elif event.startswith("deathEnemy"):
                yield from eventDeath2(data)

            elif event.startswith("death"):
                yield from eventDeath1(data)
                
            if event == "left":
                yield from eventLeft(data)


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
    loop.run_until_complete(client.run(discordToken))
except Exception:
    loop.run_until_complete(client.close())
finally:
    loop.close()






