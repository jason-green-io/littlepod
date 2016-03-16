#!/usr/bin/env python

import sys
import time
sys.path.append('/minecraft')
import rcon
import json
import yaml
from slacker import Slacker
import urllib
import oauth2 as oauth

with open('/minecraft/host/config/server.yaml', 'r') as configfile:
    config = yaml.load(configfile)


mcfolder = config['mcdata']
ConsumerKey = config['ConsumerKey']
ConsumerSecret = config['ConsumerSecret']
AccessToken = config['AccessToken']
AccessTokenSecret = config['AccessTokenSecret']

config = '/minecraft/host/config'

def send(command):
    with open("/minecraft/vanillabean", "w", 0) as f:
        print(">> " + repr(command))
        f.write(command + "\n")

def oauth_req( url, key, secret, http_method="GET", post_body="", http_headers=None ):
    consumer = oauth.Consumer( key=ConsumerKey , secret=ConsumerSecret )
    token = oauth.Token( key=key, secret=secret )
    client = oauth.Client( consumer, token )
    (resp,content) = client.request( url, method=http_method, body=post_body, headers=http_headers )
    return content


def tweet( string ):
    tweetmessage = urllib.urlencode({"status": string})
    response = json.loads(oauth_req( "https://api.twitter.com/1.1/statuses/update.json?" + tweetmessage, AccessToken, AccessTokenSecret, http_method="POST"))
    print response

def oldsend(command):
    host, port, password = ("127.0.0.1", 25575, "babybee")
    print u"Server >> " + repr(command)
    client = rcon.client(host, port, password)
    response = client.send(command)

    client.disconnect()

    print u"Server << " +repr( response)
    return repr(response)

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

