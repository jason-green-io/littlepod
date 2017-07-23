#!/usr/bin/python3
from bokeh.plotting import figure, output_file, show
from bokeh.resources import INLINE
from bokeh.embed import file_html
from bokeh.palettes import Inferno256
import sqlite3
import datetime
import sys
import codecs
import collections
sys.path.append("/minecraft")
import littlepod_utils

def getData():


    results = littlepod_utils.dbQuery(littlepod_utils.dbfile, 120, ('SELECT name, strftime("%Y-%m-%d %H:30:00", datetime) AS datetimegroup,  sum(getStat(stats, "stat.playOneMinute")) FROM playeractivity NATURAL JOIN playerUUID WHERE stats IS NOT NULL GROUP BY name, datetimegroup ORDER BY datetimegroup DESC', ))
    print(results[0:10])

    players = [each[0] for each in results]
    datetimes = [datetime.datetime.strptime(each[1], "%Y-%m-%d %H:%M:%S") for each in results]
    ticks = [each[2] for each in results]

    uniquePlayers = list(reversed(list(collections.OrderedDict.fromkeys(players))))

    dictUniquePlayers = dict([(x[1], x[0]) for x in enumerate(uniquePlayers, 1)])

    num = [dictUniquePlayers[x] for x in players]

    return uniquePlayers, datetimes, num, ticks

def graphData():
    names, x, y, ticks = getData()

    milperhour = 60 * 60 * 1000

    latest = x[0].timestamp() * 1000

    p = figure(title="Player activity",
               plot_width=800,
               plot_height=20 * len(names),
               x_axis_type="datetime",
               x_axis_location="above",
               x_range=(latest - 14 * 24 * milperhour, latest + 6 * milperhour),
               y_range=names,
               tools="xpan,xwheel_zoom,box_zoom,reset")

    print(max(ticks))

    def clamp(n, minn, maxn):
            return max(min(maxn, n), minn)
        
    colors = [Inferno256[clamp(int(x/281.25), 0, 255)] for x in ticks]

    
    p.rect(x,
           y,
           milperhour,
           0.5,
           color=colors,
           alpha=0.5,
           )

    html = file_html(p, INLINE, littlepod_utils.name + " player activity")

    codecs.open(littlepod_utils.webdata + "/activity.html", "w", "utf-8").write(html)


graphData()
