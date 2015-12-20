# encoding:utf-8
import sys
import re
import yaml
import subprocess
from slacker import Slacker
sys.path.append('/minecraft')
import showandtellraw
import vanillabean
import sqlite3

crontable = []
crontable.append( [300, "updateusers"])
crontable.append( [60, "notifymaildrops"])
outputs = []

with open('/minecraft/host/config/server.yaml', 'r') as configfile:
    config = yaml.load(configfile)


dbfile = config['dbfile']
mcfolder = config['mcdata']
URL = config['URL']
servername = config['name']
slackadminusers = config['slackadminusers']
slackadminchans = config['slackadminchans']
slackchan = config['slackchan']



slackconfig = yaml.load(file('/minecraft/python-rtmbot/rtmbot.conf', 'r'))
token = slackconfig["SLACK_TOKEN"]
slack = Slacker( token )
#slack = Slacker( "xoxb-5189863816-slDjc50BZI7XxGZwY2nmDTqu" )

members = { member["id"] : member["name"] for member in slack.users.list().body["members"] }

print members.items()

def jsonquotes( string ):
    return string.replace('"', '\\"')


def updateusers():
    global members

    members = { member["id"] : member["name"] for member in slack.users.list().body["members"] }
    conn = sqlite3.connect(dbfile)
    cur = conn.cursor()

    for each in members.items():
        cur.execute("INSERT OR REPLACE INTO slackusers VALUES (?,?)", each)

    conn.commit()
    conn.close()
    # print members



def coordsmessage( coords ):
    worlddict = { "o" : ["overworld", "0"], "n" : ["nether", "2"], "e" : ["end", "1"] }
    message =[]
    for each in coords:
        print each, each[0], each[1], each[2]

        message.append( ">Map: " + worlddict[ each[0].lower() ][0] + " " + each[1] + ', ' + each[2] + "\n>http://" + URL + "/map/#/" + each[1] + "/64/" + each[2] + "/-3/" + worlddict[ each[0].lower() ][1]  + "/0" )

    return " ".join( message )



def notifymaildrops():
    dimdict = { "n" : "2" , "e" : "1", "o" : "0" }

    conn = sqlite3.connect(dbfile)
    cur = conn.cursor()

    cur.execute("SELECT * FROM newmaildrops")

    newmaildrops = cur.fetchall()
    for each in newmaildrops:
        print each

        ID, coords = each
        dim, x, y, z = coords.split(',')
        chanID = slack.im.open(ID).body["channel"]["id"]
        outputs.append([chanID, 'Maildrop for you at ' + " ".join([dim[0] ,  x , y , z]) + '\nhttp://' + URL + '/map/#/' + x  + '/' + y + '/' + z + '/-1/' + dimdict[ dim[0] ] + '/0'])

        cur.execute("UPDATE maildrop SET notified=1 WHERE coords = ?", (coords,))

    conn.commit()
    conn.close()


def process_message( data ):
    if "reply_to" not in data and data["channel"] == slackchan:
        yup = []
        for each in data["text"].split():
            if each[0] == '<' and each[-1] =='>':
                word = each.strip('<>')
                if word[0] == "@":
                    yup.append(u"§6" + members[word.lstrip("@")] + u"§r")
                elif word[0] == "!":
                    yup.append(u"§6everyone§r")
                elif word[0] == "#":
                    yup.append(u"channel")
                else:
                    yup.append(word)
            else:
                yup.append(each)

        message = " ".join(yup)


        sendtext = formattext(u"<" + members[ data["user"] ] + u"> " + message)
        print repr(sendtext)
        vanillabean.send(sendtext)

        coordscomma = re.findall("^([OENoen]) (-?\d+), (-?\d+)", data["text"])
        if coordscomma:
            print coordscomma
            tellcoords( coordscomma )
            outputs.append( [slackchan, coordsmessage( coordscomma ) ] )

        links = re.findall('<(https?://\S+)>', data["text"])
        print links
        if links:
            telllinks( links )

    elif data["channel"] in slackadminchans and data["user"] in slackadminusers:
        outputs.append([data["channel"], vanillabean.send(data["text"].strip("."))])


def formattext( message ):

    slacktext =  u'{"text" : "#", "color" : "dark_purple" }'
    finalline = u'/tellraw @a {"text" : "", "extra" : [' + slacktext + ',' + '{ "text" : " ' + jsonquotes(message) + '"}]}'
    print type(finalline)
    return finalline


def telllinks( links ):
    for each in links:
        print each
        vanillabean.send("/tellraw @a " + showandtellraw.tojson("<green^" + servername + "> [_Link_|" + each + "]"))



def tellcoords( coords ):
    worlddict = { "o" : ["overworld", "0"], "n" : ["nether", "2"], "e" : ["end", "1"] }

    for each in coords:
        print each, each[0], each[1], each[2]

        vanillabean.send("/tellraw @a " + showandtellraw.tojson("<green^" + servername + "> [Map: _" + worlddict[ each[0].lower() ][0] + " " + each[1] + ', ' + each[2] +  "_|http://" + URL + "/map/#/" + each[1] + "/64/" + each[2] + "/-3/" + worlddict[ each[0].lower() ][1]  + "/0]"))
