import yaml
import sys
sys.path.append('/minecraft')

import overviewer_chestactivity
import overviewer_maildropdb
import overviewer_transpo
sys.path.append('/minecraft/host/config')

from overviewerconfig import *

with open('/minecraft/host/config/server.yaml', 'r') as configfile:
    config = yaml.load(configfile)

name = config["name"]





markersOverworld = markers + overviewer_maildropdb.markersover + overviewer_chestactivity.overmarker+ overviewer_transpo.overmarker
markersEnd = markers + overviewer_maildropdb.markersend + overviewer_chestactivity.endmarker+ overviewer_transpo.endmarker
markersNether = markers + overviewer_maildropdb.markersnether + overviewer_chestactivity.nethermarker+ overviewer_transpo.nethermarker




manualpoisover = spawnpoi + overviewer_transpo.polys()
manualpoisend = overviewer_transpo.polys()
manualpoisnether = overviewer_transpo.polys()



renders["north"] = {
    "world": name,
    "title": "North",
    "rendermode" : smooth_lighting,
    'dimension' : 'overworld',
    "northdirection" : "upper-left",
    'markers': markersOverworld,
    'manualpois' : manualpoisover
}
renders["end"] = {
    "world": name,
    "title": "North",
    "northdirection" : "upper-left",
    'markers': markersEnd ,
    'rendermode' : end_smooth_lighting,
    'dimension' : 'end',
    'manualpois' : manualpoisend
}
renders["nether"] = {
    "world": name,
    "title": "North",
    "northdirection" : "upper-left",
    'markers': markersNether ,
    'rendermode' : nether,
    'dimension' : 'nether',
    'manualpois' : manualpoisnether
}
