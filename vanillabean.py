#!/usr/bin/env python

import sys
sys.path.append('/minecraft')
import rcon
import json
import yaml
from slacker import Slacker

with open('/minecraft/host/config/server.yaml', 'r') as configfile:
    config = yaml.load(configfile)


mcfolder = config['mcdata']

config = '/minecraft/host/config'

def send(command):
    host, port, password = ("127.0.0.1", 25575, "babybee")
    print u"Server >> " + repr(command)
    client = rcon.client(host, port, password)
    response = client.send(command.encode('utf-8'))

    client.disconnect()

    print u"Server << " +repr( response)
    return response


def slack(string):

    config = yaml.load(file(config + '/rtmbot.conf', 'r'))
    token = config["SLACK_TOKEN"]
    slack = Slacker( token )
    chanID = slack.im.open("U056203SZ").body["channel"]["id"]
    slack.chat.post_message(chanID, string, as_user=True)


def getplayers():
    players = []
    with open(mcfolder + '/whitelist.json', 'r') as infile:
        players = [ player[ 'name' ].lower() for player in json.load( infile ) ]
    return players


if __name__ == "__main__":
    send(sys.argv[1])

