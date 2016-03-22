#!/usr/bin/env python

import io
import sys
import time
sys.path.append('/minecraft')
import json
import yaml
import urllib.parse
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
    with io.open("/minecraft/vanillabean", "w", encoding='utf-8') as file:
        print(command.encode('utf-8'))
        final = command + u"\n"
        file.write(final)

def oauth_req( url, key, secret, http_method="GET", post_body="", http_headers=None ):
    consumer = oauth.Consumer( key=ConsumerKey , secret=ConsumerSecret )
    token = oauth.Token( key=key, secret=secret )
    client = oauth.Client( consumer, token )
    (resp,content) = client.request( url, method=http_method, body=post_body, headers=http_headers )
    return content


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

