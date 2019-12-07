#!/usr/bin/python3 -u
import logging
import json
import os
import codecs
import stat
import time
import random
import re
import requests
import sys
import discord
from discord.ext import tasks, commands
import showandtellraw
import uuid
import littlepod_utils
import turtlesin


logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)

datafolder = os.environ.get('DATAFOLDER', "/minecraft/data/")
serverType = os.environ.get('TYPE', "mc")
serverVersion = os.environ.get('MCVERSION', "Unknown")

URL = os.environ.get('SERVERURL', "https://localhost/")
servername = os.environ.get('SERVERNAME', "Littlepod")
updateRoles = os.environ.get("UPDATEROLES", False)
webfolder = os.environ.get('WEBDATA', "/minecraft/shared/web/www/Littlepod")

discordChannel = int(os.environ.get("DISCORDCHANNEL", ""))
discordPrivChannel = int(os.environ.get("DISCORDPRIVCHANNEL", ""))
discordToken = os.environ.get("DISCORDTOKEN", "")
discordBannerChannel = int(os.environ.get("DISCORDBANNERCHANNEL", ""))
discordInfoChannel = int(os.environ.get("DISCORDINFOCHANNEL", ""))

if not all([discordChannel, discordPrivChannel, discordToken, discordBannerChannel, discordInfoChannel]):
    logging.critical("Not all env variables are set")
    sys.exit(1)


serverFormat = "§9\<§a{}§9\>§r"
playerFormat = "§9\<§f{}§9\>§r"
patronFormat = "§9\<§c{}§9\>§r"

mcTellraw = "tellraw {selector} {json}"
bdsTellraw = 'tellraw {selector} {{"rawtext":{json}}}'

if serverType == "mc":
    tellrawCommand = mcTellraw
elif serverType == "bds":
    tellrawCommand = bdsTellraw

if not discordToken:
    print("Discord token not set")
    sys.exit()


dimColors = {"575757": "overworld", "overworld": "575757", "3E1A19": "nether", "nether": "3E1A19", "C2C688": "end", "end": "C2C688"}

worlddict = { "o" : ["overworld", "0"], "n" : ["nether", "2"], "e" : ["end", "1"] }
channelobject = discord.Object(id=discordChannel)
privchannelobject = discord.Object(id=discordPrivChannel)

bot = commands.Bot(command_prefix='$')

brailleOrds = [chr(58)] + [chr(x) for x in range(10241, 10241 + 255)]

emojis = []
currentPlayers = []

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
        logging.info("Found link: %s", each)
        littlepod_utils.send(tellrawCommand.format(selector="@a", json=showandtellraw.tojson((serverFormat + " [_Link_|{}]").format(servername, each))))


def coordsmessage( reCoords, reDim ):
    worlddict = { "o" : ["overworld", "0"], "n" : ["nether", "2"], "e" : ["end", "1"] }

    for each in reCoords:
        logging.info("Coords, %s, %s", each[0], each[1])
        x, z = each
        message = "Map: {dim} {x}, {z}\n{URL}/map/{dim}/#zoom=0.02&x={x}&y={z}".format(dim=worlddict[reDim][0], x=x, z=z, URL=URL)

    return message


def tellcoords( reCoords, reDim ):
    worlddict = { "o" : ["overworld", "0"], "n" : ["nether", "2"], "e" : ["end", "1"] }
    for each in reCoords:
        x, z = each
        littlepod_utils.send(tellrawCommand.format(selector="@a", json=showandtellraw.tojson(serverFormat.format(servername) + " [Map: _{dim} {x}, {z}_|{URL}/map/{dim}/#zoom=0.02&x={x}&y={z}]".format(dim=worlddict[reDim][0], x=x, z=z, URL=URL))))

class serverLoop(commands.Cog):
    def __init__(self, bot):
        logging.info("Init server loop")
        self.server = bot.get_guild(140194383118073856)
        self.serverTask.start()
        self.bot = bot
        s = littlepod_utils.minecraftConsole()
        s.connect()
        self.events = s.events
        self.discordchannelobject = bot.get_channel(discordChannel)
        self.privchannelobject = bot.get_channel(discordPrivChannel)

    @tasks.loop(seconds=1)
    async def serverTask(self):
        def getgeo(ip):
            FREEGEOPIP_URL = 'http://ip-api.com/json/'
            url = '{}/{}'.format(FREEGEOPIP_URL, ip)

            response = requests.get(url)
            response.raise_for_status()
            return response.json()

        async def eventIp(data):
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
            await self.discordchannobject.send("`{}` !!!DENIED!!! {}".format(name, ipstat))


        async def eventDeath1(data):
            player = data[1]
            player = re.sub(r"\?\d(.*)\?r",r"\1", player)
            message = data[2:]
            
            await self.discordchannelobject.send("⏸ `{}` {}".format(player, "".join(message)))

        async def eventDeath2(data):
            player = data[1]
            player = re.sub(r"\?\d(.*)\?r",r"\1", player)
            message = list(data[2:])
            message[1] = "`{}`".format(message[1])
            await self.discordchannelobject.send("⏸ `{}` {}".format(player, "".join(message)))


        async def eventDeath3(data):
            player = data[1]
            player = re.sub(r"\?\d(.*)\?r",r"\1", player)
            message = list(data[2:])
            message[1] = "`{}`".format(message[1])
            message[1] = re.sub(r"\?\d(.*)\?r",r"\1", message[1])
            message[3] = "`{}`".format(message[3])
            await self.discordchannelobject.send("⏸ `{}` {}".format(player, "".join(message)))


        async def eventLogged(data):
            server =  bot.get_guild("140194383118073856")
            player = data[1]
            player = re.sub(r"\?\d(.*)\?r",r"\1", player)
            await self.discordchannelobject.send("▶️ `{}` joined the game".format(player))
            
            ip = data[2].split(':')[0]
            
            if ip:

                message = "joined"
                try:
                    hostaddr = socket.gethostbyaddr( ip )[0]
                except:
                    hostaddr = "none"
                ipinfo = getgeo( ip )
                cc = ipinfo.get("countryCode", "XX")
                ipstat= u" ".join( [ip, hostaddr, cc, str(ipinfo.get("regionName", "??")), str(ipinfo.get("city", "??")), str(ipinfo.get("as", "??")) ] )

                await self.privchannelobject.send("`{}` {}".format(player, ipstat))

        async def eventWhitelistAdd(data):
            player = data[1]
            await self.privchannelobject.send("`{}` {}".format(player, "added to whitelist"))

        async def eventWhitelistRemove(data):
            player = data[1]
            await self.privchannelobject.send("`{}` {}".format(player, "removed from whitelist"))






        async def eventUUID(data):
            player = data[1]

            UUID = data[2]


        async def eventLeft(data):
            player = data[1]
            player = re.sub(r"\?\d(.*)\?r",r"\1", player)
            await self.discordchannelobject.send("⏹ `{}` left the game".format(player))



        async def eventChat(data):

            links = re.findall('<(https?://\S+)>', data[2])

            player = data[1]
            message = data[2]

            if player == "greener_ca" and message == "die":
                assert False

            for each in re.findall("@\S+", message):
                memberfrommc = each.lstrip("@")
                # print(memberfrommc)
                member = discord.utils.find(lambda m: m.name == memberfrommc, bot.get_all_members())
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
                await self.discordchannelobject.send(finalmessage)


            reCoords =  re.findall( "(-?\d+), ?(-?\d+)", message)

            logging.info("Found coords: %s", reCoords)
            if reCoords:
                reDim = re.findall("nether|end|over| o | e | n ", message)
                if reDim:

                    if reDim[0] in ["over", " o "]:
                        dim = "o"
                    elif reDim[0] in ["nether", " n "]:
                        dim = "n"
                    elif reDim[0] in ["end", " e "]:
                        dim = "e"
                else:
                    dim = "o"


                await self.discordchannelobject.send(coordsmessage( reCoords, dim ))
                tellcoords(reCoords, dim)


        while self.events:
            event, data = self.events.pop()
            print("events:", event)
            
            if event == "UUID":
                await eventUUID(data)

            if event == "chat":
                await eventChat(data)

            if event in ["logged", "loggedbds"]:
                await eventLogged(data)

            if event == "ip":
                await eventIp(data)

            if event.startswith("deathWeapon"):
                await eventDeath3(data)

            elif event.startswith("deathEnemy"):
                await eventDeath2(data)

            elif event.startswith("death"):
                await eventDeath1(data)

            elif event.startswith("whitelistAdd"):
                await eventWhitelistAdd(data)

            elif event.startswith("whitelistRemove"):
                await eventWhitelistRemove(data)

            if event in ["left", "lost", "leftbds"]:
                await eventLeft(data)

class mainLoop(commands.Cog):
    def __init__(self, bot):
        logging.info("Init main loop")
        self.server = bot.get_guild(140194383118073856)
        self.mainTask.start()
        self.emojis = {e.name: e for e in bot.emojis}
        self.bot = bot
        self.infochannelobject = bot.get_channel(discordInfoChannel)


    def cog_unload(self):
        self.mainTask.cancel()

    @tasks.loop(minutes=1)
    async def mainTask(self):

        logging.info("Running main loop")
        info = open(datafolder + "/info.md", "r").read()

        activity = turtlesin.getActivity()

        infoFinal = info + "\n" + activity
        
        allMessages = await self.infochannelobject.history( limit=200, after=None).flatten()
        if allMessages:
            for message in allMessages:
                if message.author == self.bot.user:
                    await message.edit(content=infoFinal)
        else:
            await infochannelobject.send(infoFinal)


        '''
            allroles = [r for r in server.roles if len(r.name) == 32]

            allmembers = list(bot.get_all_members())
            for r in allroles:
                for m in allmembers:
                    if r in m.roles:
                    if m.nick:
                    if len(m.nick) < 17:
            print(m.nick + toBraille(r.name))
            await bot.change_nickname(m, m.nick + toBraille(r.name))
            elif len(m.name) < 17:
        print(m.name + toBraille(r.name))
        await bot.change_nickname(m, m.name + toBraille(r.name))
        '''
        if serverType == "mc":
            discordWhitelistedPlayers = {}
            discordWhitelistedPlayersIGN = {}

            mcWhitelistedPlayersUUID = littlepod_utils.getWhitelist()
            mcWhitelistedPlayersIGN = littlepod_utils.getWhitelistByIGN()

        for member in self.server.members:
            if "whitelisted" in [role.name for role in member.roles]:
                brailleUUID = member.nick[-16:]
                #print(member.nick, brailleUUID)
                memberUUID = fromBraille(brailleUUID)
                #print(memberUUID)


                discordWhitelistedPlayers[memberUUID] =  member.id
                discordWhitelistedPlayersIGN[mcWhitelistedPlayersUUID.get(memberUUID, "").lower()] = member

        mcWhitelistedPlayersUUID = littlepod_utils.getWhitelist()
        mcWhitelistedPlayersIGN = littlepod_utils.getWhitelistByIGN()

        add = set(discordWhitelistedPlayers) - set(mcWhitelistedPlayersUUID)
        remove = set(mcWhitelistedPlayersUUID) - set(discordWhitelistedPlayers)

        playerStatus = littlepod_utils.getPlayerStatus(whitelist=discordWhitelistedPlayers)
        if updateRoles:

            for each in playerStatus["expired"]:
                logging.info("Expired %s %s", each, mcWhitelistedPlayersUUID.get(each,""))


            for each in add:
                addIGN = littlepod_utils.getNameFromAPI(each)
                logging.info("Adding %s from the whitelist", addIGN)
                littlepod_utils.send("/whitelist add {}".format(addIGN))


            for each in remove:
                removeIGN = mcWhitelistedPlayersUUID.get(each,"")
                logging.info("Removing %s from the whitelist", removeIGN)
                littlepod_utils.send("/whitelist remove {}".format(removeIGN))

            bannerChannel = bot.get_channel(discordBannerChannel)
            try:
                with open(os.path.join(webfolder, "papyri.json"), "r") as bannerFile:
                    papyriBanners = {"{}, {}".format(b["x"], b["z"]): b for b in json.load(bannerFile)}
            except:
                papyriBanners = {}

            # print(papyriBanners)

            allChannelBanners = {message async for message in bannerChannel.history(limit=200, after=None) if message.author == bot.user}

            # print(channelBanners)
            channelBanners = {}
            for each in allChannelBanners:
                for embed in each.embeds:
                    #print(embed)

                    match = re.search("\[([0-9 \-,]*)\]", embed.description)
                    coords = match.group(1)
                    channelBanners.update({coords: each})

            # print("channel: ", channelBanners)

            dupes = allChannelBanners - set(channelBanners.values())

            addBanners = set(papyriBanners) - set(channelBanners)
            removeBanners = set(channelBanners) - set(papyriBanners)

            def IGNtoMention( match ):
                return discordWhitelistedPlayersIGN[match.group(1).lower()].mention

            for each in addBanners:
                logging.info("adding banner %s", each)
                b = papyriBanners[each]
                title = b["title"]
                title = re.sub("@([a-zA-Z0-9_]*)", IGNtoMention, title)
                description = "{} {} [{}, {}]({}/{})".format(str(emojis[b["color"] + "banner"]), title, b["x"], b["z"], URL, b["maplink"])
                colour = int(dimColors[b["dim"]], 16)
                embed = discord.Embed(description=description, colour=colour)
                logging.info(description)
                await bannerChannel.send(embed=embed)

            for each in removeBanners:
                logging.info("removing banner %s", each)
                await bot.delete_message(channelBanners[each])

            for each in dupes:
                logging.info("removing dup banner %s", each.embeds[0]["description"])
                await bot.delete_message(each)

        versionDict = {"mc": "mc:je", "bds": "mc"}
        version = versionDict[serverType] + " " + serverVersion

        if serverType == "mc":
            players = littlepod_utils.getOnlinePlayers()
            playerList = " ".join(players) if players else ""
            topicLine = "{} w/ {}".format(version, playerList)
        elif serverType == "bds":
            topicLine = version



            # print(playerList)
        await bot.change_presence(activity=discord.Game(name=topicLine))



'''
@bot.async_event
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

@bot.event
async def on_status(member, old_game, old_status):
    logging.info("%s %s %s", old_status, member.name, member.status)


@bot.event
async def on_message(message):
    logging.info("Message: %s", message)
    # we do not want the bot to reply to itself
    if message.author == bot.user:
        return
    # print(message.author.display_name, message.clean_content.encode("utf-8"), message.attachments)

    # print("mentioned", message.author)
    if bot.user in message.mentions:
        adminRole = [role for role in message.guild.roles if role.name == "admin"][0]
        if adminRole in message.author.roles and not message.author.bot:
            print("admin mention" + message.content)
            adds = re.findall( "<@!?\d*> add <@!?(\d*)> (.*)", message.content)
            logging.info("adding player: %s", adds)
            if adds:

                addDiscordID, addIGN = adds[0]
                r = requests.get('https://api.mojang.com/users/profiles/minecraft/{}'.format(addIGN))
                rDict = r.json()
                UUID = rDict["id"]
                UUIDBraille = toBraille(UUID)
                newNickname = rDict["name"] + UUIDBraille
                logging.info("nicknameing: %s %s", rDict, newNickname)

                member = server.get_member(addDiscordID)

                bot.change_nickname(member, newNickname)

                whitelistedRole = [role for role in server.roles if role.name == "whitelisted"][0]

                memberRoles = {role for role in member.roles}
                if whitelistedRole not in memberRoles:

                    bot.add_roles(member, whitelistedRole)
                    privchannelobject.send(str(rDict) + newNickname)

        if "list" in message.content:
            delMessage = message.channel.send(" ".join(['`{}`'.format(name) for name in currentPlayers]))
            asyncio.sleep(10)
            bot.delete_message(delMessage)
            bot.delete_message(message)

    reCoords =  re.findall( "(-?\d+), ?(-?\d+)", message.content)

    if reCoords:
        reDim = re.findall("nether|end|over| o | e | n ", message.content)
        if reDim:

                if reDim[0] in ["over", " o "]:
                    dim = "o"
                elif reDim[0] in ["nether", " n "]:
                    dim = "n"
                elif reDim[0] in ["end", " e "]:
                    dim = "e"
        else:
            dim = "o"

        logging.info("coords to Discord %s %s", reCoords, reDim)

        await message.channel.send(coordsmessage( reCoords, dim ))
        tellcoords(reCoords, dim)





    if message.channel.id == discordChannel:
        links = re.findall('(https?://\S+)', message.content)

        display_name = str(message.author.display_name)
        discordName = str(message.author)
        messagetext = str(message.clean_content)

        # messagetext = messagetext.replace('"', r"\"")
        discordtext =  u'{"text" : "\u2689 ", "color" : "blue" }'


        if message.author.bot:
            nameFormat = '§9\<{{§a{}~{}}}§9\>§r '
            mcplayer, mcmessage = messagetext.split(" ", 1)
            messagetext = mcplayer.strip('`') + " " + mcmessage
        elif "patrons" in [a.name for a in message.author.roles]:

            nameFormat = '§9\<{{§c{}~{}}}§9\>§r '
        else:
            nameFormat = '§9\<{{§f{}~{}}}§9\>§r '

        #finalline = '/tellraw @a[team=!mute] {{"text" : "", "extra" : [{}, {{"color" : "gold", "text" : "{} "}}, {{"text" : "{}"}}]}}'.format(discordtext, display_name, messagetext)
        tellrawText =  nameFormat.format(display_name.replace("_", "\_").replace("~",""), discordName.replace("_", "\_").replace("@","\@").replace("~",""))
        finalline = tellrawCommand.format(selector="@a", json=showandtellraw.tojson(tellrawText, noparse=messagetext))
        logging.info(finalline)

        littlepod_utils.send(finalline)


        if links:
           telllinks( links )


@bot.event
async def on_ready():
    logging.info('Logged in as %s %s', bot.user.name, bot.user.id)
    bot.add_cog(mainLoop(bot))
    bot.add_cog(serverLoop(bot))




bot.run(discordToken)


