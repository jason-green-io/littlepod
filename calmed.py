import struct
import sys
import logging
import datetime
import glob
import os
import json

logger = logging.getLogger("region_read")
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
logger.addHandler(ch)

regionGradient = ["#fb0004","#f70008","#f3000c","#ef0010","#eb0014","#e70018","#e4001b","#e0001f","#dc0023","#d80027","#d4002b","#d0002f","#cc0033","#c80037","#c4003b","#c0003f","#bc0043","#b80047","#b4004b","#b1004e","#ad0052","#a90056","#a5005a","#a1005e","#9d0062","#990066","#95006a","#91006e","#8d0072","#890076","#85007a","#81007e","#7e0081","#7a0085","#760089","#72008d","#6e0091","#6a0095","#660099","#62009d","#5e00a1","#5a00a5","#5600a9","#5200ad","#4e00b1","#4b00b4","#4700b8","#4300bc","#3f00c0","#3b00c4","#3700c8","#3300cc","#2f00d0","#2b00d4","#2700d8","#2300dc","#1f00e0","#1b00e4","#1800e7","#1400eb","#1000ef","#0c00f3","#0800f7","#0400fb"];

dimDict = {-1: "nether",
           0: "overworld",
           1: "end",
           "nether": -1,
           "overworld": 0,
           "end": 1}

# same but for the dimension paths
regionDict = {"region": 0,
              "DIM1/region": 1,
              "DIM-1/region": -1,
              0: "region",
              1: "DIM1/region",
              -1: "DIM-1/region"}

outputPath = "/web"
inputPath = "/data/mc/world"


def parseRegionHeader(regionFile):
    with open(regionFile, "rb") as f:
        header = f.read(8 * 1024)
    filename = os.path.split(regionFile)[1]
    
    regionX, regionZ = filename.split(".")[1:3]

    chunkOffsetsRaw = struct.iter_unpack('4s', header[0:4096])
    timestampsRaw = struct.iter_unpack('>I', header[4096:])

    chunkOffsets = []
    timestamps =[datetime.datetime.fromtimestamp(t[0]) for t in timestampsRaw]

    for each in chunkOffsetsRaw:
        data = each[0]
        data = data[0:3] + b'\x00' + data[3:]
        chunkOffsets.append(struct.unpack('>IB', data))


    for offset in range(0, 1024):
        coords = divmod(offset, 32)
        #logger.info("coords: %s timestamp: %s chunk: %s", coords, timestamps[offset], chunkOffsets[offset])
    return max(timestamps)




def getRegionFiles():
    mcaList = [] 
    for d in [-1, 0, 1]:
        files = glob.glob(os.path.join(inputPath, regionDict[d], "*.mca"))
        for f in files:
            regionResult = parseRegionHeader(f)
            age = datetime.datetime.now() - regionResult
            name = f.rsplit("/")[-1]
            mca = {"name": name, "age": age.days, "dim": d}
            logger.info("%s", mca)
            mcaList.append(mca)
    
    return mcaList


def genKeepMcaFiles(banners):
    """return list of mca files to keep based on marked banners"""
    # a set that only keep unique regions
    keep = set()

    # iterate over all the banners
    for banner in banners:
        # get the region coordinates base on the banner coordinates
        X = banner["X"] >> 9
        Z = banner["Z"] >> 9
        # and the dimension
        dim = dimDict[banner["dimension"]]
        # add the region files within a 5 * 5 area of the region
        for Xkeep in range(X - 2, X + 3):
            for Zkeep in range(Z - 2, Z + 3):
                keep.add((dim, Xkeep, Zkeep))
    return keep

def genRegionMarkers(mcaFileList, outputFolder, keepMcaFiles):
    regionList = []
    for mcaFile in mcaFileList:
        Xregion, Zregion = mcaFile["name"].split(".")[1:3]
        width = 512
        Xregion = int(Xregion)
        Zregion = int(Zregion)
        
        X = Xregion * width
        Z = Zregion * width
        
        age = mcaFile["age"]
        dimension = mcaFile["dim"]
        filename = "{}/r.{}.{}.mca".format(regionDict[dimension], Xregion, Zregion) 
        
        if (dimension, Xregion, Zregion) in keepMcaFiles:
            protected = True
            color = "blue"
        else:
            protected = False
            if age > 63:
                color = "black"
            else:
                color = regionGradient[age]
        

        TL = [X, Z]
        TR = [X, Z + width]
        BL = [X + width, Z + width]
        BR = [X + width, Z]

        coordinates = [[TL, TR, BL, BR, TL]]
        
        style = {"fill": color}

        properties = {"protected": protected,
                      "dimension": dimDict[dimension],
                      "age": age,
                      "filename": filename}
        
        geometry = {"type": "Polygon",
                    "coordinates": coordinates}
        
        feature = {"type": "Feature",
                   "properties": properties,
                   "geometry": geometry}
        
        regionList.append(feature)
        
    with open(os.path.join(outputFolder, "custom.json"), "+w", encoding="utf-8") as f:
        f.write(json.dumps(regionList))

if __name__ == "__main__":

    mcaFileList = getRegionFiles()
    with open(outputPath + "/banners.json") as f:
        banners = json.load(f)
    print(banners)
    keepMcaFiles = genKeepMcaFiles(banners)
    print(keepMcaFiles)
    genRegionMarkers(mcaFileList, outputPath, keepMcaFiles)
