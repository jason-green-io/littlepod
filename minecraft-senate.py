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
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

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
email = config['email']
emailpass = config['emailpass']


serverFormat = "<blue^\<><green^{}><blue^\>>"
playerFormat = "<blue^\<><white^{}><blue^\>>"
patronFormat = "<blue^\<><red^{}><blue^\>>"

discordChannel = config["discordChannel"]
discordChannel = "279672345483018242"
discordPrivChannel = config["discordPrivChannel"]
discordToken = config["discordToken"]

if not discordToken:
    print("Discord token not set")
    sys.exit()


channelobject = discord.Object(id=discordChannel)




client = discord.Client()


def dbQuery(db, timeout, query):
    conn = sqlite3.connect(db)
    results = ""
    for x in range(0, timeout):
        try:
            with conn:
                cur = conn.cursor()
                cur.execute(*query)
                results = cur.fetchall()
        except sqlite3.OperationalError:
            print("Try {} - Locked".format(x))
            time.sleep(random.random())
            pass
        finally:
            break
    else:
        with conn:
            cur = conn.cursor()
            cur.execute(*query)
            results = cur.fetchall()

    return results

@client.async_event
def create_application(q1, q2, q3, ign):
    
    application = yield from client.send_message(channelobject, content="""Application

*IGN:* {}

*Passion and hobbies:*

{}

*Intentions:*

{}

*Other:*

{}

*Status:* `Voting`
""".format(ign, q1, q2, q3))
    yield from client.pin_message(application)
    yield from client.add_reaction(application, u"\U0001f44d")
    yield from client.add_reaction(application,  u"\U0001f44e")
    
    return application


@client.async_event
def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return
    print(message.author.display_name, message.clean_content.encode("utf-8"), message.attachments)


    if message.channel.id == discordChannel:

        display_name = str(message.author.display_name)
        discordName = str(message.author)
        messagetext = str(message.clean_content) 
        if "new" in messagetext:
            yield from check_sheet()

        print([a.name for a in message.author.roles])
        
@asyncio.coroutine
def check_sheet():
    scope = ['https://spreadsheets.google.com/feeds']

    credentials = ServiceAccountCredentials.from_json_keyfile_name('/minecraft/host/config/My Project-66fa66082aaa.json', scope)


    
    global channelobject

    yield from client.wait_until_ready()
    while not client.is_closed:
        gc = gspread.authorize(credentials)
        wks = gc.open("Barlynaland application (Responses)")
        rows = wks.get_worksheet(0).get_all_values()

        newapplications = [row for row in enumerate(rows) if row[1][0] and not row[1][6]]
        oldapplications = [row for row in enumerate(rows) if row[1][6] and not row[1][7]]

        for application in newapplications:
            app = application[1]
            appmessage = yield from create_application(app[3], app[4], app[5], app[1])
            print(application[0])
            wks.get_worksheet(0).update_cell(application[0] + 1, 7, appmessage.id)

        for application in oldapplications:
            app = application[1]
            message = yield from client.get_message(channelobject, app[6])
            voteCount = 4
            upVotes = [react.count for react in message.reactions if react.emoji == u"\U0001f44d"][0]
            downVotes = [react.count for react in message.reactions if react.emoji == u"\U0001f44e"][0]
            ign = app[1]
            playeremail = app[2]

            if upVotes >= voteCount:
                print("Accepted")
                wks.get_worksheet(0).update_cell(application[0] + 1, 8, "Accepted")
                new_content = message.content.splitlines()
                new_content[-1] = "*Status:* `Accepted`"
                new_content = "\n".join(new_content)
                yield from client.edit_message(message, new_content)
                yield from client.unpin_message(message)

                fromaddr = "barlynaland@greener.ca"
                toaddr = playeremail
                msg = MIMEMultipart()
                msg['From'] = fromaddr
                msg['To'] = toaddr
                msg['Subject'] = "Tesseract Minecraft Network"

                body = """Welcome to the network, you've been whitelisted.

    This will give you access to Barlynaland, Blackbrane and Barbarus.

    Be sure to read the server message on Barlynaland when you log in, the underlined text is clickable!

    glhf

    greener_ca

    :)
    """
                msg.attach(MIMEText(body, 'plain'))


                server = smtplib.SMTP('smtp.gmail.com', 587)
                server.starttls()
                server.login(email, emailpass)

                text = msg.as_string()
                server.sendmail(fromaddr, toaddr, text)
                server.quit()
                print(playeremail)
                vanillabean.send("/whitelist add {}".format(ign))
            elif downVotes >= voteCount:
                print("Denied")
                new_content = message.content.splitlines()
                new_content[-1] = "*Status:* `Denied`"
                new_content = "\n".join(new_content)
                yield from client.edit_message(message, new_content)
                yield from client.unpin_message(message)
                wks.get_worksheet(0).update_cell(application[0] + 1, 8, "Denied")
                            
        yield from asyncio.sleep(1800)

@client.async_event
def on_ready():
    print('Logged in as')
    print((client.user.name))
    print((client.user.id))
    print('------')


        


try:
    client.loop.create_task(check_sheet())
    client.run(discordToken)   

except Exception:
    print("I crashed amd actually exited")
    client.close()
    sys.exit()






