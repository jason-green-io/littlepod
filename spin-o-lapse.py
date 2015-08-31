import json
import math
import glob
import os
import subprocess
import time

def customsorter( string ):
    return string.split("/")[-1]



def sun( angle ):
    az = 0 if angle <= 90 else 180
    al = angle if angle <= 90 else 180 - angle
    return (az, al)


# Load the default skeleton config file
config = json.load(open("skel.json", "r"))
lapse360folder = "/minecraft/spin-o-lapse"
chunky = "/minecraft/chunky.jar"
# Get the list of snapshots
#snapshotsinitial = sorted(glob.glob("/minecraft/worlddisk*/.zfs/snapshot/2015*000?"), key=customsorter)
snapshotsinitial = sorted(glob.glob("/minecraft/worlddisk*/.zfs/snapshot/2015????00??"), key=customsorter)
#snapshotsinitial = snapshotsinitial[-6480:]
num = 360
snapshotsdistributed = [snapshotsinitial[int(math.floor(deg/float(num) * len(snapshotsinitial)))] for deg in xrange(num)]
snapshots = [snapshotsdistributed[0]] * 180 + snapshotsdistributed + [snapshotsdistributed[-1]] * 180
#snapshots = snapshots[0:20]
# Coordinates of the sign
coords = ("-416", "64", "520")
spp = 20
pitch = math.radians(50)
distance = 90

# Calculate the current chunk
currentchunk = [int(coords[0]) // 16, int(coords[2]) // 16]
print currentchunk
chunkradius =  24

# Generate the list of chunks to load
chunklist = [[x, y] for x in xrange(currentchunk[0] - chunkradius, currentchunk[0] + chunkradius + 1)
             for y in xrange(currentchunk[1] - chunkradius, currentchunk[1] + chunkradius + 1)]
chunklist = [[c[0], c[1]] for c in chunklist if ((c[0] - currentchunk[0])** 2 + (c[1] - currentchunk[1]) ** 2) <= chunkradius ** 2]
# print chunklist
# Set the chunklist for Chunky
config["chunkList"] = chunklist
config["sppTarget"] = spp
config["camera"]["orientation"]["pitch"] = pitch - math.radians(90)
# Name is pased on the coordinates to keep everything separate
coordstext = "x" + coords[0] + "y" + coords[1] + "z" + coords[2]

# Set the camera to the sign coordinate
# config["camera"]["position"]["x"] = int(coords[0])
# config["camera"]["position"]["y"] = coords[1]
# config["camera"]["position"]["z"] = int(coords[2])

# Make sure the camera is pointing down

folder = lapse360folder + "/" + coordstext
if not os.path.exists(folder):
    os.makedirs(folder)

# Generate a config file for all the snapshots rotating around
numsnapshots = len(snapshots)
for snap in enumerate(snapshots):
    name = snap[1].split("/")[-1] + "." + coordstext + "." + str(snap[0]).rjust(5, "0")
    angle = snap[0] + 45
    config["name"] = name
    # print config["camera"]
    config["world"]["path"] = snap[1]
    config["camera"]["orientation"]["yaw"] = math.radians(angle)
    config["camera"]["position"]["x"] = int(coords[0]) + math.cos(math.radians(angle)) * math.cos(pitch) * distance
    config["camera"]["position"]["y"] = int(coords[1]) + math.sin(pitch) * distance
    config["camera"]["position"]["z"] = int(coords[2]) - math.sin(math.radians(angle)) * math.cos(pitch) * distance
    sunangle = snap[0] / numsnapshots * 180
    az, al = sun(sunangle)
    config["sun"]["azimuth"] = math.radians(az)
    config["sun"]["altitude"] = math.radians(al)

# print config["camera"]["orientation"], config["world"]["path"]
    # print currentfile.split("/")[-1] + name
    start = time.time()
    json.dump(config, open(folder + "/" +  name + ".json", "w"))
    command = "nice -n 2 java -jar " + chunky + " -scene-dir " + folder + "/" + " -render " + name
    subprocess.call(command, shell=True)
    subprocess.call("convert " + folder + "/" + name + "-"+str(spp)+".png -gravity southeast -stroke '#000C' -strokewidth 2 -annotate 0 \"" + name + "\" -stroke  none -fill white -annotate 0 \"" + name + "\" " + folder + "/" + name + "-annotated.png", shell=True)
    for f in glob.glob(folder + "/" + name + ".*"): os.remove(f)
    os.remove(folder + "/" + name + "-"+ str(spp) + ".png")
    stop = time.time()
    elapsed = stop - start
    print str(snap[0]) + " " + str(100.0 * (snap[0] + 1)/ numsnapshots) + " Hours left: " + str(elapsed * (numsnapshots - snap[0] + 1)/60/60)

ffmpegcommand = "ffmpeg -y -framerate 24 -pattern_type glob -i \"" + folder + "/" + "*.png\" -c:v libx264 -pix_fmt yuv420p " + folder + "/" + coordstext + ".m4v"
subprocess.call(ffmpegcommand, shell=True)
