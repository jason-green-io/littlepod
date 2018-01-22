#!/usr/bin/python3 -u
import json
import sqlite3
import asyncio
import yaml
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
import vanillabean
import showandtellraw
import uuid
import littlepod_utils

with open('/minecraft/host/config/server.yaml', 'r') as configfile:
    config = yaml.load(configfile)

name = config['name']
dbfile = config['dbfile']
mcfolder = config['mcdata']
URL = config['URL']
servername = config['name']
updateRoles = config["updateRoles"]


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



dbQuery = littlepod_utils.dbQuery


'''
def dbQuery(db, timeout, query):
    conn = sqlite3.connect(db)
    results = ""
    for x in range(0, timeout):
        try:
            with conn:
                cur = conn.cursor()
                cur.execute(*query)
                results = cur.fetchall()
        except sqlite3.OperationalError as e:
            logging.info(query)
            logging.info("Try {} - {}".format(x, e))
            time.sleep(random.random())
                                                

        finally:
            break
    else:
        with conn:
            cur = conn.cursor()
            cur.execute(*query)
            results = cur.fetchall()

    return results
'''

def telllinks( links ):
    for each in links:
        print( each)
        vanillabean.send("/tellraw @a " + showandtellraw.tojson((serverFormat + " [_Link_|{}]").format(servername, each)))


def coordsmessage( reCoords, reDim ):
    worlddict = { "o" : ["overworld", "0"], "n" : ["nether", "2"], "e" : ["end", "1"] }
    
    for each in reCoords:
        print (each[0], each[1], each[2])
        message = "Map: {} {}{}{}\n http://{}/map/#/{}/{}/{}/-3/{}/0".format(worlddict[reDim][0], each[0], each[1], each[2], URL, each[0].strip(','), each[1].strip(',') if each[1] else "64", each[2], worlddict[reDim][1] )
        #message.append( "Map: " + worlddict[ each[0].lower() ][0] + " " + each[1] + ', ' + each[2] + "\nhttp://" + URL + "/map/#/" + each[1] + "/64/" + each[2] + "/-3/" + worlddict[ each[0].lower() ][1]  + "/0" )
    
    return message


def tellcoords( reCoords, reDim ):
    worlddict = { "o" : ["overworld", "0"], "n" : ["nether", "2"], "e" : ["end", "1"] }
    for each in reCoords:
        
        vanillabean.send("/tellraw @a " + showandtellraw.tojson(serverFormat.format(servername) + "[Map: _{} {}{}{}_|http://{}/map/#/{}/{}/{}/-3/{}/0]".format(worlddict[reDim][0], each[0], each[1], each[2], URL, each[0].strip(','), each[1].strip(',') if each[1] else "64" , each[2], worlddict[reDim][1])))



def updateTopic():

    yield from client.wait_until_ready()
    server =  client.get_server("140194383118073856")
    print("Updating topic")

    worlddict = { "o" : ["overworld", "0"], "n" : ["nether", "2"], "e" : ["end", "1"] }
    while True:
        discordWhitelistedPlayers = {}
        for member in server.members:
            mRolesDict = {r.name: r  for r in member.roles}
            
            for r in mRolesDict:
                if len(r) == 32:
                    # yield from client.edit_channel_permissions(channelobject, mRolesDict[r], overwrite)
                    yield from client.edit_role(server, mRolesDict[r], colour=discord.Colour.green())
                    discordWhitelistedPlayers[str(uuid.UUID(r))] =  member.id

        
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
            vanillabean.send("/whitelist add {}".format(addIGN))
            

        for each in remove:
            removeIGN = mcWhitelistedPlayersUUID.get(each,"")
            print("Removing {} from the whitelist".format(removeIGN))
            vanillabean.send("/whitelist remove {}".format(removeIGN))
            
        players = dbQuery(dbfile, 100, ('SELECT name FROM playeractivity NATURAL JOIN playerUUID WHERE datetime > datetime("now", "-2 minutes") GROUP BY name',))

        notifymaildrops = dbQuery(dbfile, 100, ('SELECT * FROM maildrop WHERE notified = 0 AND datetime > datetime("now", "-1 day")', ()))


        for drop in notifymaildrops:

            dimcoords, boxname, desc, slots, hidden, inverted, notified, datetime = drop
            if (slots > 0 and inverted == 0) or (slots == 0 and inverted == 1):
                dim, coords = dimcoords.split(",", 1)
                        
                URLcoords = coords.replace(",", "/")           

                toplayer = ':package: {} {} http://{}/map/#/{}/-1/{}/0\n'.format(desc if desc else "{} {}".format(worlddict[dim][0], coords), "has {} items".format(slots) if slots else "is empty", URL, URLcoords, worlddict[dim][1])
          
                memberID = discordWhitelistedPlayers.get(mcWhitelistedPlayersIGN.get(boxname, ""), "")
                
                member = server.get_member(memberID)
                print(member)
                # yield from client.send_message(member, toplayer)            

                print(toplayer)

        dbQuery(dbfile, 100, ('UPDATE maildrop SET notified = 1 WHERE notified = 0', ()))

        formattedplayers = ["{}".format(a[0]) for a in players]
        channel = client.get_channel(discordChannel)
        currentTopic = channel.topic
        currentName = channel.name
        topicLineList = currentTopic.split('\n')
        #topicLine = [line for line in enumerate(topicLineList) if line[1].startswith(name)][0][0]

        #topicLineList[topicLine] = "{} - {}/20 - `({})`".format(name, len(formattedplayers), " ".join(formattedplayers))

        playerList = " ".join(formattedplayers) if formattedplayers else "*None*"
        # print(playerList)
        yield from client.change_presence(game=discord.Game(name=playerList)) 
        #yield from client.edit_channel(channel, position=1, name=currentName, topic="\n".join(topicLineList))
        print("waiting for 60 seconds")
        yield from asyncio.sleep(60)

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

    if client.user in message.mentions:
        print("mentioned")
        reCoords =  re.findall( "(-?\d+,) ?(\d+,)? ?(-?\d+)", message.content)
        
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



    
    if message.channel.is_private:

        if message.content.startswith("/"):
            command = message.content[1:].split(" ", 1)[0]
            args = message.content[1:].split(" ", 1)[1:]
            print(command, args)
            name = dbQuery(dbfile, 100, ('SELECT name FROM players WHERE discordID = ?', (message.author.id,)))
            if name:
                name = name[0][0]
                print(name, command, args)


            '''
            if command == "link":
                if args:
                    ign = args[0]

                    member = server.get_member(message.author.id)
                    yield from client.send_message(message.channel, "You have 10 seconds to connect to the server with  {}. If you are already connected, please disconnect and reconnect. You will receive a message when you are successful".format(ign))            
                    dbQuery(dbfile, 100, ('INSERT INTO verify (name, discordID) VALUES (?, ?)', (ign, message.author.id)))

            '''

            if command == "mute":
                
                if "on" in args:
                    print("yup")
                    vanillabean.send("/scoreboard teams join mute {}".format(name))
                    vanillabean.send("/tell {} Muting Discord".format(name))
                elif "off" in args:
                    vanillabean.send("/scoreboard teams leave mute {}".format(name))
                    vanillabean.send("/tell {} Un-Muting Discord".format(name))





            if command == "maildrop":
                print("Printing maildrops")
                maildrop = dbQuery(dbfile, 30, ("SELECT coords, name, desc, slots, hidden, inverted FROM maildrop WHERE name = ? COLLATE NOCASE", (name,)))
                print(maildrop)

                if maildrop:
                    toplayer = "Showing maildrops for {}\n".format(name)
                    for mail in maildrop:
                        dimcoords, boxname, desc, slots, hidden, inverted = mail
                        dim, coords = dimcoords.split(",", 1)

                        URLcoords = coords.replace(",", "/")           

                        toplayer += ':package: {} {} http://{}/map/#/{}/-1/{}/0\n'.format(desc if desc else "{} {}".format(worlddict[dim][0], coords), "has {} items".format(slots) if slots else "is empty", URL, URLcoords, worlddict[dim][1])
                    yield from client.send_message(message.channel, toplayer)            




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

        vanillabean.send(finalline)


        if links:
           telllinks( links )

    if message.channel.id == discordPrivChannel and not message.author.bot:
        if message.content.startswith("/"):
            command, args = message.content.split(' ', 1)
            command = command.strip('/')
            # print(command, args)
            if command == "link":
                manualLinkDiscordID, manualLinkIGN = args.split()
                # print(manualLinkDiscordID, manualLinkIGN)
                r = requests.get('https://api.mojang.com/users/profiles/minecraft/{}'.format(manualLinkIGN))
                rDict = r.json()
                UUID = rDict["id"]
                newNickname = rDict["name"]
                print(rDict)

                member = server.get_member(manualLinkDiscordID)

                yield from client.change_nickname(member, newNickname)
                currentRoles = {role.name: role for role in server.roles}
                if UUID not in currentRoles:
                    
                    newRole = yield from client.create_role(server, name=UUID)
                else:
                    newRole = currentRoles[UUID]

                
                yield from client.edit_channel_permissions(channelobject, newRole, overwrite)
                yield from client.add_roles(member, newRole)
                yield from client.send_message(privchannelobject, rDict)
        

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
    
    try:
        for each in open( otherdata + "/motd.txt", "r" ).readlines():

            time.sleep(1)
            message = "/tellraw " + player + " " + showandtellraw.tojson( each.strip() )
            vanillabean.send( message )
    except:
        pass
    ip = data[2].split(':')[0]

    message = "joined"
    try:
        hostaddr = socket.gethostbyaddr( ip )[0]
    except:
        hostaddr = "none"
    ipinfo = getgeo( ip )
    cc = ipinfo.get("countryCode", "XX")
    ipstat= u" ".join( [ip, hostaddr, cc, str(ipinfo.get("regionName", "??")), str(ipinfo.get("city", "??")), str(ipinfo.get("as", "??")) ] )
    dbQuery(dbfile, 100, ('UPDATE players SET lastIP=?, country=? WHERE name=?', (ip, cc, player)))
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
    dbQuery(dbfile, 100, ('UPDATE players SET name=? WHERE UUID=?', (player, UUID)))
    dbQuery(dbfile, 100, ('INSERT OR IGNORE INTO players (name, UUID) VALUES (?, ?)',(player, UUID)))

    
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


    reCoords =  re.findall( "(-?\d+,) ?(\d+,)? ?(-?\d+)", message)
        
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
            eventData = vanillabean.genEvent(line)
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

def handle_updateTopic():

    try:
        print("Starting update topic handler")
        yield from updateTopic()
    except Exception:
        print("Topic handler exception")
        client.close()
        sys.exit(1)

        
loop = asyncio.get_event_loop()

try:

    client.loop.create_task(handle_bgtask())
    client.loop.create_task(handle_updateTopic())
    client.run(discordToken)   
   
except Exception:
    print("I crashed amd actually exited")
    client.close()
    sys.exit()






