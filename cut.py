#!/usr/bin/python3
"""
dimension@x0,y0,x1,y1+x0,y0,x1,y1 dimension@x0,y0,x1,x1
"""
import os
import glob
import random
import logging
import argparse
import sys

dims = sys.argv[1:]
print(dims)
if not dims:
    logging.warning("Nothing to do")
    sys.exit(0)
regionDict = {"0": "region", "1": "DIM1/region", "-1": "DIM-1/region"}

for dimRanges in dims:
    dim, ranges = dimRanges.split("@")
    safeRanges = ranges.split("+")
    safeRanges = [r.split(",") for r in safeRanges]
    logging.warning("Saving regions %s", safeRanges)

    region = os.path.join(os.environ["DATAFOLDER"], "mc/world", regionDict[dim])

    mcaFiles = glob.glob(region + "/*.mca")
    safeFiles = []

    for each in safeRanges:

        safeFiles += ["{}/r.{}.{}.mca".format(region, x, z) for x in range(int(each[0]), int(each[2]) + 1) for z in range(int(each[1]), int(each[3]) + 1) ]

    deletable = []
    for f in mcaFiles:
        if f in safeFiles:
            pass
        else:
            deletable.append(f)
        
    numFiles = len(deletable)
    numToDelete = numFiles * 0.75

    numToDelete = int(numToDelete) if numToDelete >= 1 else 1


    if deletable:
        logging.warning("Out of %s, randomly deleting %s", numFiles, numToDelete)
        deleteFiles = random.sample(deletable, numToDelete)


        for each in deleteFiles:
            logging.warning("Deleting file %s", each)
            os.remove(each)
    else:
        logging.warning("Nothing to delete")
