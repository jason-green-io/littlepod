#!/usr/bin/env python3

import re
import io
import sys
import time
sys.path.append('/minecraft')
import json
import yaml
import urllib.parse
import oauth2 as oauth
from collections import OrderedDict

with open('/minecraft/host/config/server.yaml', 'r') as configfile:
    config = yaml.load(configfile)


mcfolder = config['mcdata']
ConsumerKey = config['ConsumerKey']
ConsumerSecret = config['ConsumerSecret']
AccessToken = config['AccessToken']
AccessTokenSecret = config['AccessTokenSecret']

config = '/minecraft/host/config'

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


def send(command):
    with open("/minecraft/vanillabean", "w", encoding='utf-8') as file:
        # print(command)
        final = command + u"\n"
        file.write(final)

def oauth_req( url, key, secret, http_method="GET", post_body="", http_headers=None ):
    consumer = oauth.Consumer( key=ConsumerKey , secret=ConsumerSecret )
    token = oauth.Token( key=key, secret=secret )
    client = oauth.Client( consumer, token )
    (resp,content) = client.request( url, method=http_method, body=post_body, headers=http_headers )
    return content

def genEvent(line):
	parseDict = OrderedDict([("deathFloorLava", "^\[(.*)\] \[Server thread/INFO\]: (.*)(  discovered floor was lava)$"),
                                 ("deathSquashAnvil", "^\[(.*)\] \[Server thread/INFO\]: (.*)( was squashed by a falling anvil)$"),
                                 ("deathSquashBlock", "^\[(.*)\] \[Server thread/INFO\]: (.*)( was squashed by a falling block)$"),
                                 ("deathFlames", "^\[(.*)\] \[Server thread/INFO\]: (.*)( went up in flames)$"),
                                 ("deathBurned", "^\[(.*)\] \[Server thread/INFO\]: (.*)( burned to death)$"),
                                 ("deathShot", "^\[(.*)\] \[Server thread/INFO\]: (.*)( was shot by arrow)$"),
                                 ("deathWithered", "^\[(.*)\] \[Server thread/INFO\]: (.*)( withered away)$"),
                                 ("deathPricked", "^\[(.*)\] \[Server thread/INFO\]: (.*)( was pricked to death)$"),
                                 ("deathDrowned", "^\[(.*)\] \[Server thread/INFO\]: (.*)( drowned)$"),
                                 ("deathKinetic", "^\[(.*)\] \[Server thread/INFO\]: (.*)( experienced kinetic energy)$"),
                                 ("deathBlewUp", "^\[(.*)\] \[Server thread/INFO\]: (.*)( blew up)$"),
                                 ("deathHitGround", "^\[(.*)\] \[Server thread/INFO\]: (.*)( hit the ground too hard)$"),
                                 ("deathHighPlace", "^\[(.*)\] \[Server thread/INFO\]: (.*)( fell from a high place)$"),
                                 ("deathLadder", "^\[(.*)\] \[Server thread/INFO\]: (.*)( fell off a ladder)$"),
                                 ("deathVines", "^\[(.*)\] \[Server thread/INFO\]: (.*)( fell off some vines)$"),
                                 ("deathWater", "^\[(.*)\] \[Server thread/INFO\]: (.*)( fell out of the water)$"),
                                 ("deathIntoFire", "^\[(.*)\] \[Server thread/INFO\]: (.*)( fell into a patch of fire)$"),
                                 ("deathIntoCactus", "^\[(.*)\] \[Server thread/INFO\]: (.*)( fell into a patch of cacti)$"),
                                 ("deathLava", "^\[(.*)\] \[Server thread/INFO\]: (.*)( tried to swim in lava)$"),
                                 ("deathLightning", "^\[(.*)\] \[Server thread/INFO\]: (.*)( was struck by lightning)$"),
                                 ("deathStarved", "^\[(.*)\] \[Server thread/INFO\]: (.*)( starved to death)$"),
                                 ("deathSuffocated", "^\[(.*)\] \[Server thread/INFO\]: (.*)( suffocated in a wall)$"),
                                 ("deathVoid", "^\[(.*)\] \[Server thread/INFO\]: (.*)( fell out of the world)$"),
                                 ("deathHighVoid", "^\[(.*)\] \[Server thread/INFO\]: (.*)( fell from a high place and fell out of the world)$"),
                                 ("deathMagic", "^\[(.*)\] \[Server thread/INFO\]: (.*)( was killed by magic)$"),
                                 ("deathWeaponSlain", "^\[(.*)\] \[Server thread/INFO\]: (.*)( was slain by )(.*)( using )(.*)$"),
                                 ("deathWeaponShot", "^\[(.*)\] \[Server thread/INFO\]: (.*)( was shot by )(.*)( using )(.*)$"),
                                 ("deathWeaponFinished", "^\[(.*)\] \[Server thread/INFO\]: (.*)( got finished off by )(.*)( using )(.*)$"),
                                 ("deathEnemyFloorLava", "^\[(.*)\] \[Server thread/INFO\]: (.*)( walked into danger zone due to )(.*)$"),
                                 ("deathEnemyBlewUp", "^\[(.*)\] \[Server thread/INFO\]: (.*)( was blown up by )(.*)$"),
                                 ("deathEnemyDrowned", "^\[(.*)\] \[Server thread/INFO\]: (.*)( drowned whilst trying to escape )(.*)$"),
                                 ("deathEnemyIntoCactus", "^\[(.*)\] \[Server thread/INFO\]: (.*)( walked into a cactus while trying to escape )(.*)$"),
                                 ("deathEnemyShot", "^\[(.*)\] \[Server thread/INFO\]: (.*)( was shot by )(.*)$"),
                                 ("deathEnemyDoomed", "^\[(.*)\] \[Server thread/INFO\]: (.*)( was doomed to fall by )(.*)$"),
                                 ("deathEnemyVines", "^\[(.*)\] \[Server thread/INFO\]: (.*)( was shot off some vines by )(.*)$"),
                                 ("deathEnemyLadder", "^\[(.*)\] \[Server thread/INFO\]: (.*)( was shot off a ladder by )(.*)$"),
                                 ("deathEnemyBlewUpHigh", "^\[(.*)\] \[Server thread/INFO\]: (.*)( was blown from a high place by )(.*)$"),
                                 ("deathEnemyBurnt", "^\[(.*)\] \[Server thread/INFO\]: (.*)( was burnt to a crisp whilst fighting )(.*)$"),
                                 ("deathEnemyFire", "^\[(.*)\] \[Server thread/INFO\]: (.*)( walked into a fire whilst fighting )(.*)$"),
                                 ("deathEnemyDrowned", "^\[(.*)\] \[Server thread/INFO\]: (.*)( tried to swim in lava while trying to escape )(.*)$"),
                                 ("deathEnemySlain", "^\[(.*)\] \[Server thread/INFO\]: (.*)( was slain by )(.*)$"),
                                 ("deathEnemyFinished", "^\[(.*)\] \[Server thread/INFO\]: (.*)( got finished off by )(.*)$"),
                                 ("deathEnemyFireballed", "^\[(.*)\] \[Server thread/INFO\]: (.*)( was fireballed by )(.*)$"),
                                 ("deathEnemyMagic", "^\[(.*)\] \[Server thread/INFO\]: (.*)( was killed by )(.*)( using magic)$"),
                                 ("deathEnemyHurt", "^\[(.*)\] \[Server thread/INFO\]: (.*)( was killed while trying to hurt )(.*)$"),
                                 ("deathEnemyPummeled", "^\[(.*)\] \[Server thread/INFO\]: (.*)( was pummeled by )(.*)$"),
                                 ("joined", "^\[(.*)\] \[Server thread/INFO\]: (.*) joined the game$"),
                                 ("left", "^\[(.*)\] \[Server thread/INFO\]: (.*) left the game$"),
                                 ("lost", "^\[(.*)\] \[Server thread/INFO\]: (.*) lost.*"),
                                 ("logged", "^\[(.*)\] \[Server thread/INFO\]: (.*)\[/(.*)\] logged in.*$"),
                                 ("ip", "^\[(.*)\] \[Server thread/INFO\]: Disc.*name=(.*),pro.*\(/(.*)\).*$"),
                                 ("command", "^\[(.*)\] \[Server thread/INFO\]: \<(.*)\> !(.*)$"),
                                 ("chat", "^\[(.*)\] \[Server thread/INFO\]: \<(.*)\> (.*)$"),
                                 ("playerList", "^\[(.*)\] \[Server thread/INFO]: There are (.*)/(.*) players online:$"),
                                 ("muteTeam", "^\[(.*)\] \[Server thread/INFO]: Showing (.*) player\(s\) in team mute:$"),
                                 ("UUID", "^\[(.*)\] \[User Authenticator #.*/INFO\]: UUID of player (.*) is (.*)$"),
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


if __name__ == "__main__":
    send(sys.argv[1])

