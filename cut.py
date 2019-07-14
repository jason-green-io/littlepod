import sys
import os
import glob
import datetime
import littlepod_utils
import logging

logging.basicConfig(level=logging.DEBUG)

dataFolder = os.environ["DATAFOLDER"]

worldFolder  = os.path.join(dataFolder, "mc", "world")

files = {a: datetime.datetime.fromtimestamp(os.stat(a).st_mtime) for a in glob.glob(os.path.join(worldFolder, "*/*.mca"))}

'''

- something:
   - 0,20,0
   - -1,30,0
- bla:
    - 70,45

- yup:
    - 60,87
'''

buildRegions = littlepod_utils.configbook("6060debe-836f-4a45-95ab-4311a53972f7", "fade")
#buildRegions = littlepod_utils.configbook("967cae4f-c09e-4ac0-aaff-bfc9b4e34778", "fade")
regionDict = {"0": "region", "-1": "DIM-1", "1": "DIM1"}


buildRegionFiles = set()
expiredRegionFiles = set()

if buildRegions:

    for permit in buildRegions:
        for name, drList in permit.items():
            logging.info("%s %s", name, drList)
            for dr in drList:
                d, x, z = dr.split(',')
                buildRegionFiles.add("{}/{}/r.{}.{}.mca".format(worldFolder, regionDict[d], x, z))

for f in files.items():
    if f[1] <= datetime.datetime.now() - datetime.timedelta(days=64):
        expiredRegionFiles.add(f[0])


logging.info("Build permit regions %s", len(buildRegionFiles))

#for a in buildRegionFiles:
#    logging.info(a)

logging.info("Expired regions %s", len(expiredRegionFiles))

#for a in expiredRegionFiles:
#    logging.info(a)

deleteRegionFiles = expiredRegionFiles - buildRegionFiles


logging.info("Deletable regions %s", len(deleteRegionFiles))

#for a in deleteRegionFiles:
#    logging.info(a)
