#!/usr/bin/python3 -u
import json
import sqlite3
import asyncio
import os
import codecs
import stat
import time
import random
import re
import requests
import sys
import discord
sys.path.append('/minecraft/discord.py')
import showandtellraw
import uuid
import littlepod_utils

mcfolder = os.environ.get('MCDATA', "/minecraft/host/mcdata")
URL = os.environ.get('SERVERURL', "https://localhost/")
servername = os.environ.get('SERVERNAME', "Littlepod")
updateRoles = os.environ.get("UPDATEROLES", False)
webfolder = os.environ.get('WEBDATA', "/minecraft/shared/web/www/Littlepod")

discordChannel = os.environ.get("DISCORDCHANNEL", "")
discordPrivChannel = os.environ.get("DISCORDPRIVCHANNEL", "")
discordToken = os.environ.get("DISCORDTOKEN", "")
discordBannerChannel = os.environ.get("DISCORDBANNERCHANNEL", "")

serverFormat = "<blue^\<><green^{}><blue^\>>"
playerFormat = "<blue^\<><white^{}><blue^\>>"
patronFormat = "<blue^\<><red^{}><blue^\>>"

if not discordToken:
    print("Discord token not set")
    sys.exit()


channelobject = discord.Object(id=discordChannel)
privchannelobject = discord.Object(id=discordPrivChannel)

overwrite = discord.PermissionOverwrite()
overwrite.read_messages = True
overwrite.send_messages = True
overwrite.embed_links = True
overwrite.attach_files = True
overwrite.read_message_history = True
overwrite.mention_everyone = True
overwrite.external_emojis = True
overwrite.add_reactions = True

serverrestart = False

client = discord.Client()

brailleOrds = [chr(58)] + [chr(x) for x in range(10241, 10241 + 255)]

#print(brailleOrds) 


def custom_exception_handler(loop, context):
    # first, handle with default handler
    loop.default_exception_handler(context)
    exception = context.get('exception')
    print(context)
    loop.stop()


def toBraille( inputuuid ):
    uuidBytes = uuid.UUID("{{{}}}".format(inputuuid)) 
    ords = [ord(brailleOrds[x]) for x in uuidBytes.bytes]
    #print(ords)
    return "".join([chr(x) for x in ords])

def fromBraille( braille ):
    ords = [brailleOrds.index(x) for x in braille]
    #print(ords)
    uuidBytes = bytes(ords)
    # print(uuidBytes)
    return str(uuid.UUID(bytes=uuidBytes))


def telllinks( links ):
    for each in links:
        print( each)
        littlepod_utils.send("/tellraw @a " + showandtellraw.tojson((serverFormat + " [_Link_|{}]").format(servername, each)))


def coordsmessage( reCoords, reDim ):
    worlddict = { "o" : ["overworld", "0"], "n" : ["nether", "2"], "e" : ["end", "1"] }
    
    for each in reCoords:
        print (each[0], each[1])
        x, z = each
        message = "Map: {dim} {x}, {z}\n{URL}/map/{dim}/#zoom=0.02&x={x}&y={z}".format(dim=worlddict[reDim][0], x=x, z=z, URL=URL)
    
    return message


def tellcoords( reCoords, reDim ):
    worlddict = { "o" : ["overworld", "0"], "n" : ["nether", "2"], "e" : ["end", "1"] }
    for each in reCoords:
        x, z = each
        littlepod_utils.send("/tellraw @a " + showandtellraw.tojson(serverFormat.format(servername) + "[Map: _{dim} {x}, {z}_|{URL}/map/{dim}/#zoom=0.02&x={x}&y={z}]".format(dim=worlddict[reDim][0], x=x, z=z, URL=URL)))



async def updateTopic():

    await client.wait_until_ready()
    server =  client.get_server("140194383118073856")
    print("Updating topic")
    emojis = {e.name: e for e in client.get_all_emojis()}
    print(emojis)
    worlddict = { "o" : ["overworld", "0"], "n" : ["nether", "2"], "e" : ["end", "1"] }
    
    allroles = [r for r in server.roles if len(r.name) == 32]

    allmembers = list(client.get_all_members())
    '''
    for r in allroles:
        for m in allmembers:
            if r in m.roles:
                if m.nick:
                    if len(m.nick) < 17:
                        print(m.nick + toBraille(r.name))
                        await client.change_nickname(m, m.nick + toBraille(r.name))
                elif len(m.name) < 17:
                    print(m.name + toBraille(r.name))
                    await client.change_nickname(m, m.name + toBraille(r.name))
    '''
    while True:
        discordWhitelistedPlayers = {}
        for member in server.members:
            if "whitelisted" in [role.name for role in member.roles]:
                brailleUUID = member.nick[-16:]
                #print(member.nick, brailleUUID)
                memberUUID = fromBraille(brailleUUID)
                #print(memberUUID)
            
                
                discordWhitelistedPlayers[memberUUID] =  member.id

        
        mcWhitelistedPlayersUUID = littlepod_utils.getWhitelist()
        mcWhitelistedPlayersIGN = littlepod_utils.getWhitelistByIGN()
        
        add = set(discordWhitelistedPlayers) - set(mcWhitelistedPlayersUUID)
        remove = set(mcWhitelistedPlayersUUID) - set(discordWhitelistedPlayers)

        playerStatus = littlepod_utils.getPlayerStatus(whitelist=discordWhitelistedPlayers)
        if updateRoles:

            for each in playerStatus["expired"]:
                print("Expired {} {}".format(each, mcWhitelistedPlayersUUID.get(each,"")))
            

        for each in add:
            addIGN = littlepod_utils.getNameFromAPI(each)
            print("Adding {} from the whitelist".format(addIGN))
            littlepod_utils.send("/whitelist add {}".format(addIGN))
            

        for each in remove:
            removeIGN = mcWhitelistedPlayersUUID.get(each,"")
            print("Removing {} from the whitelist".format(removeIGN))
            littlepod_utils.send("/whitelist remove {}".format(removeIGN))
            
        players = littlepod_utils.getOnlinePlayers()
        version = littlepod_utils.getVersion()

        bannerChannel = client.get_channel(discordBannerChannel)
        try: 
            with open(os.path.join(webfolder, "papyri.json"), "r") as bannerFile:
                papyriBanners = {"{} {}, {}".format(b["dim"], b["x"], b["z"]): b for b in json.load(bannerFile)} 
        except:
            papyriBanners = {}
        
        print(papyriBanners)    
        
        channelBanners = {message.content.split("\n")[1]: message async for message in client.logs_from(bannerChannel, limit=200, after=None) if message.author == client.user}

        print(channelBanners)
        
        addBanners = set(papyriBanners) - set(channelBanners)
        removeBanners = set(channelBanners) - set(papyriBanners)
        print("add {}".format(addBanners))
        print("remove {}".format(removeBanners))
        
        for each in addBanners:
            b = papyriBanners[each]
            message = "{} {}\n{} {}, {}\n{}/{}".format(str(emojis[b["color"] + "banner"]), b["title"], b["dim"], b["x"], b["z"], URL, b["maplink"])
            await client.send_message(bannerChannel, message)
        
        for each in removeBanners:
            await client.delete_message(channelBanners[each])
        
        playerList = " ".join(players) if players else ""
        
        topicLine = "{} w/ {}".format(version, playerList)
        
        # print(playerList)
        await client.change_presence(game=discord.Game(name=topicLine)) 
        
        
        
        
        
        
        
        
        print("waiting for 60 seconds")
        await asyncio.sleep(60)

'''
@client.async_event
def on_member_update(before, after):

    beforeRoles = [role.name for role in before.roles]
    afterRoles = [role.name for role in after.roles]
    # print(beforeRoles, afterRoles)
    player = before.nick if before.nick else before.name
    if "whitelisted" in beforeRoles and "whitelisted" not in afterRoles:
        print("Unwhitelisting")
        vanillabean.send("/whitelist remove {}".format(player))
    elif "whitelisted" not in beforeRoles and "whitelisted" in afterRoles:
        print("Whitelisting")
        vanillabean.send("/whitelist add {}".format(player))
'''
        
@client.async_event
def on_status(member, old_game, old_status):
    print(old_status)
    print(member.name)
    print(member.status)

@client.async_event
def on_message(message):
    server =  client.get_server("140194383118073856")
    worlddict = { "o" : ["overworld", "0"], "n" : ["nether", "2"], "e" : ["end", "1"] }
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return
    # print(message.author.display_name, message.clean_content.encode("utf-8"), message.attachments)
    
    print("mentioned", message.author)
    if client.user in message.mentions:
        adminRole = [role for role in server.roles if role.name == "admin"][0]
        if adminRole in message.author.roles and not message.author.bot:
            print("admin mention" + message.content)
            adds = re.findall( "<@!?\d*> add <@!?(\d*)> (.*)", message.content)
            print(adds)
            if adds:
                
                addDiscordID, addIGN = adds[0]
                r = requests.get('https://api.mojang.com/users/profiles/minecraft/{}'.format(addIGN))
                rDict = r.json()
                UUID = rDict["id"]
                UUIDBraille = toBraille(UUID)
                newNickname = rDict["name"] + UUIDBraille
                print(rDict, newNickname)

                member = server.get_member(addDiscordID)

                yield from client.change_nickname(member, newNickname)
                
                whitelistedRole = [role for role in server.roles if role.name == "whitelisted"][0]
                
                memberRoles = {role for role in member.roles}
                if whitelistedRole not in memberRoles:

                    yield from client.add_roles(member, whitelistedRole)
                    yield from client.send_message(privchannelobject, str(rDict) + newNickname)


        reCoords =  re.findall( "(-?\d+), ?(-?\d+)", message.content)
        
        print(reCoords)
        if reCoords:
            reDim = re.findall("nether|end|over| o | e | n ", message.content)
            print(reDim)
            if reDim:
    
                if reDim[0] in ["over", " o "]:
                    dim = "o"
                elif reDim[0] in ["nether", " n "]:
                    dim = "n"
                elif reDim[0] in ["end", " e "]:
                    dim = "e"
            else:
                dim = "o"

                
            yield from client.send_message(message.channel, coordsmessage( reCoords, dim ))
            tellcoords(reCoords, dim)



    

    if message.channel.id == discordChannel:
        links = re.findall('(https?://\S+)', message.content)

        display_name = str(message.author.display_name)
        discordName = str(message.author)
        messagetext = str(message.clean_content) 
        # messagetext = messagetext.replace('"', r"\"")
        discordtext =  u'{"text" : "\u2689 ", "color" : "blue" }'

        print([a.name for a in message.author.roles])
        
        if message.author.bot:
            nameFormat = '<blue^\<>{{<green^{}>~{}}}<blue^\>> '
            mcplayer, mcmessage = messagetext.split(" ", 1)
            messagetext = mcplayer.strip('`') + " " + mcmessage
        elif "patrons" in [a.name for a in message.author.roles]:
            
            nameFormat = '<blue^\<>{{<red^{}>~{}}}<blue^\>> '
        else:
            nameFormat = '<blue^\<>{{<white^{}>~{}}}<blue^\>> '

        #finalline = '/tellraw @a[team=!mute] {{"text" : "", "extra" : [{}, {{"color" : "gold", "text" : "{} "}}, {{"text" : "{}"}}]}}'.format(discordtext, display_name, messagetext)
        tellrawText =  nameFormat.format(display_name.replace("_", "\_").replace("~",""), discordName.replace("_", "\_").replace("@","\@").replace("~",""))
        finalline = '/tellraw @a[team=!mute] ' + showandtellraw.tojson(tellrawText, noparse=messagetext)

        littlepod_utils.send(finalline)


        if links:
           telllinks( links )

                    

@client.async_event
def on_ready():
    print('Logged in as')
    print((client.user.name))
    print((client.user.id))
    print('------')
    global server

    yield from client.send_message(discord.Object(id=discordPrivChannel),"I crashed, but I'm back now.") 

def getgeo(ip):
    FREEGEOPIP_URL = 'http://ip-api.com/json/'
    url = '{}/{}'.format(FREEGEOPIP_URL, ip)

    response = requests.get(url)
    response.raise_for_status()
    # print(response.json)
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
    if not ipinfo["status"] == "fail":
        ipstat = " ".join( [ip, hostaddr, ipinfo.get("countryCode", "??"), str(ipinfo.get("regionName", "??")), str(ipinfo.get("city", "??")), str(ipinfo.get("as", "??")) ] )
    else:
        ipstat = " ".join([ip, hastaddr])
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
    server =  client.get_server("140194383118073856")
    player = data[1]
    player = re.sub(r"\?\d(.*)\?r",r"\1", player)
    yield from client.send_message(channelobject, "`{}` joined the server".format(player))

    ip = data[2].split(':')[0]

    message = "joined"
    try:
        hostaddr = socket.gethostbyaddr( ip )[0]
    except:
        hostaddr = "none"
    ipinfo = getgeo( ip )
    cc = ipinfo.get("countryCode", "XX")
    ipstat= u" ".join( [ip, hostaddr, cc, str(ipinfo.get("regionName", "??")), str(ipinfo.get("city", "??")), str(ipinfo.get("as", "??")) ] )

    yield from client.send_message(privchannelobject, "`{}` {}".format(player, ipstat))

@asyncio.coroutine
def eventWhitelistAdd(data):
    player = data[1]
    yield from client.send_message(privchannelobject, "`{}` {}".format(player, "added to whitelist"))

@asyncio.coroutine
def eventWhitelistRemove(data):
    player = data[1]
    yield from client.send_message(privchannelobject, "`{}` {}".format(player, "removed from whitelist"))

    
    
    

    
@asyncio.coroutine 
def eventUUID(data):
    server =  client.get_server("140194383118073856")
    player = data[1]

    UUID = data[2]

    
@asyncio.coroutine 
def eventLeft(data):
    player = data[1]
    player = re.sub(r"\?\d(.*)\?r",r"\1", player)
    yield from client.send_message(channelobject, "`{}` left the server".format(player))



@asyncio.coroutine 
def eventChat(data):

    links = re.findall('<(https?://\S+)>', data[2])

    player = data[1]
    message = data[2]

    if player == "greener_ca" and message == "die":
        assert False
    
    for each in re.findall("@\S+", message):
        memberfrommc = each.lstrip("@")
        # print(memberfrommc)
        member = discord.utils.find(lambda m: m.name == memberfrommc, client.get_all_members())
        if member:
            membermention = member.mention
            message = message.replace( each, membermention)
        # print(message)
    
    
    if links:
        telllinks( links )

    if not player.startswith("?7"):
        player = re.sub(r"\?\d(.*)\?r",r"\1", player)
        finalmessage = "`<{}>` {}".format(player, message)
        # print(repr(finalmessage))
        yield from client.send_message(channelobject, finalmessage)


    reCoords =  re.findall( "(-?\d+), ?(-?\d+)", message)
        
    print(reCoords)
    if reCoords:
        reDim = re.findall("nether|end|over| o | e | n ", message)
        print(reDim)
        if reDim:
    
            if reDim[0] in ["over", " o "]:
                dim = "o"
            elif reDim[0] in ["nether", " n "]:
                dim = "n"
            elif reDim[0] in ["end", " e "]:
                dim = "e"
        else:
            dim = "o"

                
        yield from client.send_message(channelobject, coordsmessage( reCoords, dim ))
        tellcoords(reCoords, dim)


@asyncio.coroutine 
def my_background_task():
    yield from client.wait_until_ready()


    serverrestart = False
    logfile = os.path.abspath(mcfolder + "/logs/latest.log")
    f = codecs.open(logfile,"r", "utf-8")
    file_len = os.stat(logfile)[stat.ST_SIZE]
    f.seek(file_len)
    pos = f.tell()

    
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
            eventData = littlepod_utils.genEvent(line)
            event = ""
            data = ()
            
            if eventData:
                # print(eventData)
                event, data = eventData
                # print(event, data)

            if event == "UUID":
                yield from eventUUID(data)
                
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
                
            elif event.startswith("whitelistAdd"):
                yield from eventWhitelistAdd(data)
                
            elif event.startswith("whitelistRemove"):
                yield from eventWhitelistRemove(data)
                
            if event == "left":
                yield from eventLeft(data)



def handle_bgtask():
    try:
        print("Starting main background task")
        yield from my_background_task()
    except Exception:
        print("Main background task exception")
        client.close()
        sys.exit(1)

try:
    client.loop.set_exception_handler(custom_exception_handler)
    client.loop.create_task(handle_bgtask())
    client.loop.create_task(updateTopic())
    client.run(discordToken)   
   
except Exception:
    print("I crashed amd actually exited")
    client.close()
    sys.exit()






