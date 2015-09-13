#!/usr/bin/python

import datetime
import time
import json
import glob
import sys
import os
import nbt2yaml
import yaml

players = json.load(open("/minecraft/usercache.json", "r"))
UUIDtoplayer = { user["uuid"] : user["name"] for user in players }

# for all in UUIDtoplayer.keys():
#     print all


def filterplayer0(poi):
    if poi['id'] == 'player0':
        return poi['name'] + '\n' + poi["datetime"] + "\n" + str(poi['x']) +" "+str(poi['y']) + " " + str(poi['z'])


def filterplayer1(poi):
    if poi['id'] == 'player1':
        return poi['name'] + '\n' + poi["datetime"] + "\n" + str(poi['x']) +" "+str(poi['y']) + " " + str(poi['z'])


def filterplayer2(poi):
    if poi['id'] == 'player2':
        return poi['name'] + '\n' + poi["datetime"] + "\n" + str(poi['x']) +" "+str(poi['y']) + " " + str(poi['z'])


def filterplayer3(poi):
    if poi['id'] == 'player3':
        return poi['name'] + '\n' + poi["datetime"] + "\n" + str(poi['x']) +" "+str(poi['y']) + " " + str(poi['z'])


def filterplayer4(poi):
    if poi['id'] == 'player4':
        return poi['name'] + '\n' + poi["datetime"] + "\n" + str(poi['x']) +" "+str(poi['y']) + " " + str(poi['z'])


player0 = [ dict(name="Player Activity - today", icon="icons/xpgreen.png", filterFunction=filterplayer0, createInfoWindow=True, checked=False)]
player1 = [ dict(name="Player Activity - yesterday", icon="icons/xpyellow.png", filterFunction=filterplayer1, createInfoWindow=True, checked=False)]
player2 = [ dict(name="Player Activity - 2 days ago", icon="icons/xporange.png", filterFunction=filterplayer2, createInfoWindow=True, checked=False)]
player3 = [ dict(name="Player Activity - 3 days ago", icon="icons/xpred.png", filterFunction=filterplayer3, createInfoWindow=True, checked=False)]
player4 = [ dict(name="Player Activity - last 31 days", icon="icons/xpred.png", filterFunction=filterplayer4, createInfoWindow=True, checked=False)]


def gettimerangefiles( start, end ):
    print "!!!"
    print "Getting files for player activity", time.strftime("%Y/%m/%d, %H:%M:%S", time.localtime(int(start))), time.strftime("%Y/%m/%d, %H:%M:%S", time.localtime(int(end)))
    files = [file for file in glob.glob("/minecraft/god/*/*.dat") if int(file.rsplit('/',1)[1].split('.')[0]) >= start and int(file.rsplit('/',1)[1].split('.')[0]) < end ]
    return files


def plotFolder( playerfiles, day ):
    print "Processing", len(playerfiles), "files for day", day
    over = []
    nether = []
    end = []

    for playerfile in playerfiles:

        nbt = nbt2yaml.parse_nbt(open( playerfile, "r" ))
        position = [ bla.data for bla in nbt.data if bla.name == "Pos"]
        dimension = [ bla.data for bla in nbt.data if bla.name == "Dimension"]
        UUIDleast =[ bla.data for bla in nbt.data if bla.name == "UUIDLeast"]
        UUIDmost =[ bla.data for bla in nbt.data if bla.name == "UUIDMost"]
        #print [ tag for tag in nbt ]
        datetimeconverted = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(float(playerfile.rsplit('/',1)[1].split('.')[0])))
        UUID =  getUUID( int(UUIDleast[0]), int(UUIDmost[0]))
        (x1, y1, z1) = position[0][1]
        x1=int(x1)
        y1=int(y1)
        z1 = int(z1)
        if dimension[0] == 0:
            over.append(  dict(id="player" + str(day), name=UUIDtoplayer[UUID], x=x1, y=y1, z=z1, datetime=datetimeconverted) )
        elif dimension[0] == -1:
            nether.append(  dict(id="player" + str(day), name=UUIDtoplayer[UUID], x=x1, y=y1, z=z1, datetime = datetimeconverted) )
        elif dimension[0] == 1:
            end.append(  dict(id="player" + str(day), name=UUIDtoplayer[UUID], x=x1, y=y1, z=z1, datetime = datetimeconverted) )

    return ( end, over, nether )


def getUUID(least, most):
        return digits(most >> 32, 8) + "-" + digits(most >> 16, 4) + "-" + digits(most, 4) + "-" + digits(least >> 48, 4) + "-" + digits(least, 12)


def digits(val, digits):
        hi = long(1) << (digits * 4)
        return hex(hi | (val & (hi-1)))[3:-1]


day = 24 * 3600
hour = 60 * 60
twenty = 20 * 60
now = int(time.time())
now = now

todayepoch = now - ( now % day )
yesterdayepoch = todayepoch - day
days2agoepoch = yesterdayepoch - day
days3agoepoch = days2agoepoch - day

endrange = int(datetime.datetime(2015,8,1).strftime("%s"))
range2 = endrange
range1 = range2 - 31 * day


specified = plotFolder( gettimerangefiles( range1, range2 ), 4 )
days3 = plotFolder( gettimerangefiles( days3agoepoch, days2agoepoch), 3 )
days2 = plotFolder( gettimerangefiles( days2agoepoch, yesterdayepoch), 2 )
yesterday = plotFolder( gettimerangefiles( yesterdayepoch, todayepoch), 1 )
today = plotFolder( gettimerangefiles( todayepoch, now), 0 )

nether = days3[2] + days2[2] + yesterday[2] + today[2] + specified[2]
over = days3[1] + days2[1] + yesterday[1] + today[1] + specified[1]
end = days3[0] + days2[0] + yesterday[0] + today[0] + specified[0]
markers = player1 + player2 + player3 + player0 + player4
