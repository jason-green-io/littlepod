#!/usr/bin/python
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

lag = [("2015-01-01 00:00:00",0)]
timeframe = "-14 days"

conn = sqlite3.connect(dbfile)

cur = conn.cursor()

cur.execute('select datetime(ts), ticks from loglag where ts > datetime("now", "{}")'.format(timeframe))
lag += cur.fetchall()

cur.execute('select * from activity where datetime > datetime("now", "{}")'.format(timeframe))
activity = cur.fetchall()
cur.execute('SELECT process, ts, end  FROM process WHERE ts > datetime("now", "{}")'.format(timeframe))
process = cur.fetchall()

conn.commit()
conn.close()

#hours = mdates.MinuteLocator(byminute=[0,30])

timespan = [datetime.datetime.now() - datetime.timedelta(days=14), datetime.datetime.now()]
hours = mdates.DayLocator()
hoursFmt = mdates.DateFormatter('%d')

if activity == []:
    activity = [("2015-01-01 00:00:00.0", "No players active")]


ax = []
fig = plt.figure()
ax0 = plt.subplot2grid((6,1), (0,0), rowspan=4)
ax1 = plt.subplot2grid((6,1), (5,0))
ax2 = plt.subplot2grid((6,1), (4,0))

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



xact, yact = tuple(zip(*activity))
xact = [datetime.datetime.strptime(time, "%Y-%m-%d %H:%M:%S.%f") for time in xact]
players = [""] + list({player for player in yact})
yact = [players.index(p) for p in yact]
xactdates = mdates.date2num(xact)
ax0.xaxis_date()
ax0.xaxis.set_major_locator(hours)
ax0.xaxis.set_major_formatter(hoursFmt)
ax0.set_xlim(timespan)
ax0.scatter(xactdates, yact, marker=".")
ax0.grid(True)
ax0.set_yticklabels(players)
ax0.set_yticks(xrange(0, len(players) + 1))
ax0.set_ylabel("player activity")

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
ax2.set_yticks(xrange(0, len(procs) + 1))


fig.set_size_inches(10.24, 20.48)
plt.tight_layout()
plt.savefig(webdata + "/stats.png",  dpi=100)

