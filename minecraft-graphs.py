#!/usr/bin/python3
import numpy as np
import matplotlib
matplotlib.use("Agg")
matplotlib.rcParams['font.family'] = 'Minecraftia'
matplotlib.rcParams['font.size'] = 10
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import yaml
import sqlite3
import datetime

with open('/minecraft/host/config/server.yaml', 'r') as configfile:
    config = yaml.load(configfile)


dbfile = config['dbfile']
webdata = config['webdata']
name = config["name"]

lag = [("2015-01-01 00:00:00",0)]
timeframe = "-14 days"
timeframe2 = "-4 months"

def getStat(stats, stat):

    if stats:
        evalStats = eval(stats)

        if type(evalStats) is dict:
            return evalStats.get(stat, 0)

conn = sqlite3.connect(dbfile)
conn.create_function("getStat", 2, getStat)
cur = conn.cursor()

cur.execute('select datetime(ts), ticks from loglag where ts > datetime("now", "{}")'.format(timeframe))
lag += cur.fetchall()

cur.execute('select datetime, name, getStat(stats, "stat.playOneMinute") from playeractivity natural join playerUUID where stats IS NOT NULL and datetime > datetime("now", "{}")'.format(timeframe))
activity = cur.fetchall()

cur.execute('select datetime, name, getStat(stats, "stat.playOneMinute") from playeractivity natural join playerUUID where stats IS NOT NULL and datetime > datetime("now", "{}")'.format(timeframe2))
activity2 = cur.fetchall()

    


cur.execute('select name, count(getStat(stats, "stat.playOneMinute")) as total from playeractivity natural join playerUUID where stats IS NOT NULL and datetime > datetime("now", "{}") group by name order by total asc'.format(timeframe))
players = cur.fetchall()

cur.execute('select name, count(getStat(stats, "stat.playOneMinute")) as total from playeractivity natural join playerUUID where stats IS NOT NULL and datetime > datetime("now", "{}") group by name order by total asc'.format(timeframe2))
players2 = cur.fetchall()



cur.execute('SELECT process, ts, end  FROM process WHERE ts > datetime("now", "{}")'.format(timeframe))
process = cur.fetchall()

conn.commit()
conn.close()

#hours = mdates.MinuteLocator(byminute=[0,30])

timespan = [datetime.datetime.now() - datetime.timedelta(days=14), datetime.datetime.now()]
timespan2 = [datetime.datetime.now() - datetime.timedelta(days=4 * 30), datetime.datetime.now()]
hours = mdates.DayLocator()
hoursFmt = mdates.DateFormatter('%d')
months = mdates.MonthLocator()
monthsFmt = mdates.DateFormatter('%m')


if activity == []:
    activity = [("2015-01-01 00:00:00.0", "No players active")]

if activity2 == []:
    activity2 = [("2015-01-01 00:00:00.0", "No players active")]


ax = []
fig = plt.figure()
figlen = len(players) + len(players2) + 10 + 10
ax0 = plt.subplot2grid((figlen,1), (0,0), rowspan=len(players))
ax0.set_title(name + " last 2 weeks")
ax1 = plt.subplot2grid((figlen,1), (len(players),0), rowspan=10)
ax1.set_title(name + " lag")
ax2 = plt.subplot2grid((figlen,1), (len(players) + 10,0), rowspan=10)
ax2.set_title(name + " process time")
ax3 = plt.subplot2grid((figlen,1), (len(players) + 20,0), rowspan=len(players2))
ax3.set_title(name + " last 4 months")

xlag, ylag = tuple(zip(*lag))
xlag = [datetime.datetime.strptime(time, "%Y-%m-%d %H:%M:%S") for time in xlag]
ylag = [int(y) for y in ylag]
xlagdates = mdates.date2num(xlag)
width = 0.00001
ax1.bar(xlagdates,ylag, width=width)
ax1.xaxis_date()
ax1.xaxis.set_major_locator(hours)
ax1.xaxis.set_major_formatter(hoursFmt)
ax1.set_ylim([0, 300])
ax1.set_xlim(timespan)
ax1.set_ylabel("ticks skipped")
ax1.grid(True)



xact, yact, area = tuple(zip(*activity))
xact = [datetime.datetime.strptime(time, "%Y-%m-%d %H:%M:%S") for time in xact]
players = [player[0] for player in players]
yact = [players.index(p) for p in yact]
xactdates = mdates.date2num(xact)
ax0.xaxis_date()
ax0.xaxis.set_major_locator(hours)
ax0.xaxis.set_major_formatter(hoursFmt)
ax0.set_xlim(timespan)
print(area[0:10])
ax0.scatter(xactdates, yact, c=area, s=25, linewidth=0, alpha=.8, marker='s', cmap="winter")

ax0.grid(True)
ax0.set_yticklabels(players)
ax0.set_yticks(range(0, len(players)))
ax0.set_ylim([-1, len(players)])
ax0.set_ylabel("player activity")



xact2, yact2, area2 = tuple(zip(*activity2))
xact2 = [datetime.datetime.strptime(time, "%Y-%m-%d %H:%M:%S") for time in xact2]
players2 = [player[0] for player in players2]
yact2 = [players2.index(p) for p in yact2]
print(players2)

xactdates2 = mdates.date2num(xact2)
ax3.xaxis_date()
ax3.xaxis.set_major_locator(months)
ax3.xaxis.set_major_formatter(monthsFmt)
ax3.set_xlim(timespan2)
print(area2[0:10])
ax3.scatter(xactdates2, yact2, c=area2, s=25, linewidth=0, alpha=.8, marker='s', cmap="winter")

ax3.grid(True)
ax3.set_yticklabels(players2)
ax3.set_yticks(range(0, len(players2)))
ax3.set_ylim([-1, len(players2)])
ax3.set_ylabel("player activity")





plt.tight_layout()

yproc, startproc, endproc = tuple(zip(*process))

endproc = [datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d %H:%M:%S") if time == None else time for time in endproc]

procs = [""] + list({proc for proc in yproc})
yproc = [procs.index(p) for p in yproc]
startproc = [datetime.datetime.strptime(time, "%Y-%m-%d %H:%M:%S") for time in startproc]
endproc = [datetime.datetime.strptime(time, "%Y-%m-%d %H:%M:%S") for time in endproc if time != '']
ax2.hlines(yproc, startproc, endproc, lw=2)
ax2.xaxis_date()
ax2.set_ylabel("server processes")
ax2.xaxis.set_major_locator(hours)
ax2.xaxis.set_major_formatter(hoursFmt)
ax2.set_xlim(timespan)
ax2.xaxis.grid(True)
ax2.set_yticklabels(procs)
ax2.set_yticks(range(0, len(procs) + 1))


fig.set_size_inches(10.24, 20.48)
plt.tight_layout()
plt.savefig(webdata + "/stats.png",  dpi=100)

