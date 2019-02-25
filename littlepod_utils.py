import datetime
import requests
import os
import json
import time
import glob
import re
import io
import sys
import urllib.parse
import oauth2 as oauth
from collections import OrderedDict
import socket
from nbt.nbt import NBTFile, TAG_Long_Array, TAG_Long, TAG_Int, TAG_String, TAG_List, TAG_Compound
import yaml

mcfolder = os.path.join(os.environ.get('DATAFOLDER', "/minecraft/data"), "mc")

'''
ConsumerKey = config['ConsumerKey']
ConsumerSecret = config['ConsumerSecret']
AccessToken = config['AccessToken']
AccessTokenSecret = config['AccessTokenSecret']
'''

mobList = ["Bat",
            "Blaze",
            "Cave Spider",
            "Chicken",
            "Chicken Jockey",
            "Cow",
            "Creeper",
            "Donkey",
            "Elder Guardian",
            "Ender Dragon",
            "Enderman",
            "Endermite",
            "Ghast",
            "Giant",
            "Guardian",
            "Horse",
            "Husk",
            "Iron Golem",
            "Killer Bunny",
            "Magma Cube",
            "Mooshroom",
            "Mule",
            "Ocelot",
            "Pig",
            "Polar Bear",
            "Rabbit",
            "Sheep",
            "Shulker",
            "Silverfish",
            "Skeleton",
            "Skeleton Horse",
            "Skeleton Horseman",
            "Slime",
            "Snow Golem",
            "Spider",
            "Spider Jockey",
            "Squid",
            "Stray",
            "Villager",
            "Witch",
            "Wither",
            "Wither Skeleton",
            "Wolf",
            "Zombie",
            "Zombie Horse",
            "Zombie Pigman",
            "Zombie Villager",
            "Vex",
            "Evoker",
            "Vindicator"]



def send(command, host="localhost", port=7777):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, int(port)))
    command += "\n"
    s.sendall(command.encode())
    s.shutdown(socket.SHUT_WR)
    while True:
        data = s.recv(4096)
        if not data:
            break
        print(repr(data))
    s.close()

def oauth_req( url, key, secret, http_method="GET", post_body="", http_headers=None ):
    consumer = oauth.Consumer( key=ConsumerKey , secret=ConsumerSecret )
    token = oauth.Token( key=key, secret=secret )
    client = oauth.Client( consumer, token )
    (resp,content) = client.request( url, method=http_method, body=post_body, headers=http_headers )
    return content

def genEvent(line):
	parseDict = OrderedDict([("deathFloorLava", "^\[(.*)\] \[Server thread/INFO\]: (.*) (discovered floor was lava)$"),
                                ("deathSquashAnvil", "^\[(.*)\] \[Server thread/INFO\]: (.*) (was squashed by a falling anvil)$"),
                                ("deathSquashBlock", "^\[(.*)\] \[Server thread/INFO\]: (.*) (was squashed by a falling block)$"),
                                ("deathFlames", "^\[(.*)\] \[Server thread/INFO\]: (.*) (went up in flames)$"),
                                ("deathBurned", "^\[(.*)\] \[Server thread/INFO\]: (.*) (burned to death)$"),
                                ("deathShot", "^\[(.*)\] \[Server thread/INFO\]: (.*) (was shot by arrow)$"),
                                ("deathWithered", "^\[(.*)\] \[Server thread/INFO\]: (.*) (withered away)$"),
                                ("deathPricked", "^\[(.*)\] \[Server thread/INFO\]: (.*) (was pricked to death)$"),
                                ("deathDrowned", "^\[(.*)\] \[Server thread/INFO\]: (.*) (drowned)$"),
                                ("deathKinetic", "^\[(.*)\] \[Server thread/INFO\]: (.*) (experienced kinetic energy)$"),
                                ("deathElytra", "^\[(.*)\] \[Server thread/INFO\]: (.*) (removed an elytra while flying)$"),
                                ("deathBlewUp", "^\[(.*)\] \[Server thread/INFO\]: (.*) (blew up)$"),
                                ("deathHitGround", "^\[(.*)\] \[Server thread/INFO\]: (.*) (hit the ground too hard)$"),
                                ("deathHighPlace", "^\[(.*)\] \[Server thread/INFO\]: (.*) (fell from a high place)$"),
                                ("deathLadder", "^\[(.*)\] \[Server thread/INFO\]: (.*) (fell off a ladder)$"),
                                ("deathVines", "^\[(.*)\] \[Server thread/INFO\]: (.*) (fell off some vines)$"),
                                ("deathWater", "^\[(.*)\] \[Server thread/INFO\]: (.*) (fell out of the water)$"),
                                ("deathIntoFire", "^\[(.*)\] \[Server thread/INFO\]: (.*) (fell into a patch of fire)$"),
                                ("deathIntoCactus", "^\[(.*)\] \[Server thread/INFO\]: (.*) (fell into a patch of cacti)$"),
                                ("deathLava", "^\[(.*)\] \[Server thread/INFO\]: (.*) (tried to swim in lava)$"),
                                ("deathLightning", "^\[(.*)\] \[Server thread/INFO\]: (.*) (was struck by lightning)$"),
                                ("deathStarved", "^\[(.*)\] \[Server thread/INFO\]: (.*) (starved to death)$"),
                                ("deathSuffocated", "^\[(.*)\] \[Server thread/INFO\]: (.*) (suffocated in a wall)$"),
                                ("deathSquish", "^\[(.*)\] \[Server thread/INFO\]: (.*) (was squished too much)$"),
                                ("deathVoid", "^\[(.*)\] \[Server thread/INFO\]: (.*) (fell out of the world)$"),
                                ("deathHighVoid", "^\[(.*)\] \[Server thread/INFO\]: (.*) (fell from a high place and fell out of the world)$"),
                                ("deathMagic", "^\[(.*)\] \[Server thread/INFO\]: (.*) (was killed by magic)$"),
                                ("deathWeaponSlain", "^\[(.*)\] \[Server thread/INFO\]: (.*) (was slain by) (.*)( using )(.*)$"),
                                ("deathWeaponShot", "^\[(.*)\] \[Server thread/INFO\]: (.*) (was shot by )(.*)( using )(.*)$"),
                                ("deathWeaponFinished", "^\[(.*)\] \[Server thread/INFO\]: (.*) (got finished off by )(.*)( using )(.*)$"),
                                ("deathEnemyFloorLava", "^\[(.*)\] \[Server thread/INFO\]: (.*) (walked into danger zone due to )(.*)$"),
                                ("deathEnemyBlewUp", "^\[(.*)\] \[Server thread/INFO\]: (.*) (was blown up by )(.*)$"),
                                ("deathEnemyDrowned", "^\[(.*)\] \[Server thread/INFO\]: (.*) (drowned whilst trying to escape )(.*)$"),
                                ("deathEnemyIntoCactus", "^\[(.*)\] \[Server thread/INFO\]: (.*) (walked into a cactus while trying to escape )(.*)$"),
                                ("deathEnemyShot", "^\[(.*)\] \[Server thread/INFO\]: (.*) (was shot by )(.*)$"),
                                ("deathEnemyDoomed", "^\[(.*)\] \[Server thread/INFO\]: (.*) (was doomed to fall by )(.*)$"),
                                ("deathEnemyVines", "^\[(.*)\] \[Server thread/INFO\]: (.*) (was shot off some vines by )(.*)$"),
                                ("deathEnemyLadder", "^\[(.*)\] \[Server thread/INFO\]: (.*) (was shot off a ladder by )(.*)$"),
                                ("deathEnemyBlewUpHigh", "^\[(.*)\] \[Server thread/INFO\]: (.*) (was blown from a high place by )(.*)$"),
                                ("deathEnemyBurnt", "^\[(.*)\] \[Server thread/INFO\]: (.*) (was burnt to a crisp whilst fighting )(.*)$"),
                                ("deathEnemyFire", "^\[(.*)\] \[Server thread/INFO\]: (.*) (walked into a fire whilst fighting )(.*)$"),
                                ("deathEnemyDrowned", "^\[(.*)\] \[Server thread/INFO\]: (.*) (tried to swim in lava while trying to escape )(.*)$"),
                                ("deathEnemySlain", "^\[(.*)\] \[Server thread/INFO\]: (.*) (was slain by )(.*)$"),
                                ("deathEnemyFinished", "^\[(.*)\] \[Server thread/INFO\]: (.*) (got finished off by )(.*)$"),
                                ("deathEnemyFireballed", "^\[(.*)\] \[Server thread/INFO\]: (.*) (was fireballed by )(.*)$"),
                                ("deathEnemyMagic", "^\[(.*)\] \[Server thread/INFO\]: (.*) (was killed by )(.*)( using magic)$"),
                                ("deathEnemyHurt", "^\[(.*)\] \[Server thread/INFO\]: (.*) (was killed while trying to hurt )(.*)$"),
                                ("deathEnemyPummeled", "^\[(.*)\] \[Server thread/INFO\]: (.*) (was pummeled by )(.*)$"),
                                ("joined", "^\[(.*)\] \[Server thread/INFO\]: (.*) joined the game$"),
                                ("left", "^\[(.*)\] \[Server thread/INFO\]: (.*) left the game$"),
                                ("lost", "^\[(.*)\] \[Server thread/INFO\]: (.*) lost.*"),
                                ("logged", "^\[(.*)\] \[Server thread/INFO\]: (.*)\[/(.*)\] logged in.*$"),
                                ("ip", "^\[(.*)\] \[Server thread/INFO\]: Disc.*name=(.*),pro.*\(/(.*)\).*$"),
                                ("command", "^\[(.*)\] \[Server thread/INFO\]: \<(.*)\> !(.*)$"),
                                ("chat", "^\[(.*)\] \[Server thread/INFO\]: \<(.*)\> (.*)$"),
                                ("playerList", "^\[(.*)\] \[Server thread/INFO]: There are (.*)/(.*) players online:$"),
                                ("UUID", "^\[(.*)\] \[User Authenticator #.*/INFO\]: UUID of player (.*) is (.*)$"),
                                ("whitelistAdd", "^\[(.*)\] \[Server thread/INFO]: Added (.*) to the whitelist"),
                                ("whitelistRemove", "^\[(.*)\] \[Server thread/INFO]: Removed (.*) from the whitelist"),
                                ("achievement", "^\[(.*)\] \[Server thread/INFO\]: (\w*) has just earned the achievement \[(.*)\]$"),
                                ("lag", "^\[(.*)\] \[Server thread/WARN\]: Can't keep up! Did the system time change, or is the server overloaded\? Running (\d*)ms behind, skipping (\d*) tick\(s\)$")])


	for pattern in parseDict.items():
		match = re.match(pattern[1], line)
		if match:
			return pattern[0], match.groups()

def tweet( string ):
    tweetmessage = urllib.parse.urlencode({"status": string})
    response = json.loads(oauth_req( "https://api.twitter.com/1.1/statuses/update.json?" + tweetmessage, AccessToken, AccessTokenSecret, http_method="POST").decode("utf-8") )
    print( response)


"""
def slack(string):

    token = config["SLACK_TOKEN"]
    slack = Slacker( token )
    chanID = slack.im.open("U056203SZ").body["channel"]["id"]
    slack.chat.post_message(chanID, string, as_user=True)
"""

def getplayers():
    players = []
    with open(mcfolder + '/whitelist.json', 'r') as infile:
        players = [ player[ 'name' ].lower() for player in json.load( infile ) ]
    return players



def unpack_nbt(tag):
    """
    Unpack an NBT tag into a native Python data structure.
    """

    if isinstance(tag, TAG_List):
        return [unpack_nbt(i) for i in tag.tags]
    elif isinstance(tag, TAG_Compound):
        return dict((i.name, unpack_nbt(i)) for i in tag.tags)
    else:
        return tag.value

def getVersion():
    nbtData = NBTFile(os.path.join(mcfolder, "world", "level.dat"))
    Obj = unpack_nbt(nbtData)
    return Obj["Data"]["Version"]["Name"]

def getOnlinePlayers():
    playerFiles = glob.glob(os.path.join(mcfolder, "world/playerdata/*.dat"))
    playerUUIDTime = [os.path.basename(f).rsplit(".")[0]  for f in playerFiles if os.path.getmtime(f) > time.time() - 300]
    whitelist = getWhitelist()
    return [whitelist[p] for p in playerUUIDTime]


def getUserCache():
    return {each["uuid"]: (datetime.datetime.strptime(each["expiresOn"][:19], "%Y-%m-%d %H:%M:%S") - datetime.timedelta(days=30), each["name"]) for each in json.load(open(mcfolder + "/usercache.json"))}

def getWhitelist():
    return {each["uuid"]: each["name"] for each in json.load(open(mcfolder + "/whitelist.json"))}

def getWhitelistByIGN():
    return {each["name"].lower(): each["uuid"] for each in json.load(open(mcfolder + "/whitelist.json"))}

def getNameFromAPI(uuid):
    return requests.get('https://api.mojang.com/user/profiles/{}/names'.format(uuid.replace('-', ''))).json()[-1].get("name", "")

def getPlayerStatus(whitelist=getWhitelist(), usercache=getUserCache()):
    expired = []
    active = []
    for each in sorted(usercache, key=usercache.get):
        if each in whitelist and usercache[each][0] <= datetime.datetime.now() - datetime.timedelta(days=120):
            # print(each, usercache[each])
            expired.append(each)


    for each in sorted(usercache, key=usercache.get):
        if each in whitelist and usercache[each][0] > datetime.datetime.now() - datetime.timedelta(days=120):
            # print(each, usercache[each])
            active.append(each)
    return {"active": active, "expired": expired}



def reduceItem( item ):
    from collections import OrderedDict
    item = dict(item)
    keyFilter = ["Count", "Slot", "id"]
    newItem = OrderedDict()

    for key in sorted(item):
        if key in keyFilter:
            newItem.update({key: item[key]})
            if key == "tag":
                if "display" in item["tag"]:
                    if "Name" in item["tag"]["display"]:
                        item.update({"Name": item["tag"]["display"]["Name"]})

    return json.dumps(newItem)


def diffChest(old, new):
    if old or new:
        oldItems = json.loads(old)
        newItems = json.loads(new)

        oldItemsReduced = [reduceItem(item) for item in oldItems]
        newItemsReduced = [reduceItem(item) for item in newItems]
        #print(oldItemsReduced)
        removed = set(oldItemsReduced) - set(newItemsReduced)
        added = set(newItemsReduced) - set(oldItemsReduced)

        removedText = "[{}]".format(", ".join(removed))
        addedText = "[{}]".format(", ".join(added))

        return "[{}, {}]".format(removedText, addedText)
    else:
        return "[[], []]"

def inSphere(x, y, z, cx, cy, cz, r):
    if x or y or z:
        return (x - cx) ** 2 + (y - cy) ** 2 + (z - cz) ** 2 < r ** 2

def getStat(stats, stat):

        if stats:
            evalStats = eval(stats)

            if type(evalStats) is dict:
                return evalStats.get(stat, 0)

def configbook(uuid, bookname):

    itemFilter = "book"

    filename = os.path.join(mcfolder, "world/playerdata/{}.dat".format(uuid))

    def getnbt(filename):
        nbtdata = NBTFile(filename)
        return unpack_nbt(nbtdata)


    Obj = getnbt(filename)

    Inv = Obj["Inventory"]
    End = Obj["EnderItems"]

    All = Inv + End

    def flatten(items):

        newItems = []

        for each in items:
            if "shulker_box" in each["id"]:
                newItems += each["tag"]["BlockEntityTag"]["Items"]
            else:
                newItems.append(each)
        return newItems

    All = flatten(All)

    Filtered = [a for a in All if itemFilter in a["id"] and a.get("tag",{}).get("display",{}).get("Name", {}) == '{{"text":"{}"}}'.format(bookname)]

    if Filtered:
        string = "\n".join(Filtered[0]["tag"]["pages"])
        return yaml.load(string)


if __name__ == "__main__":
    send(sys.argv[1])



