import json
import math
import glob
import os
import subprocess
import time
import vanillabean

def customsorter( string ):
    """
    sort on the name of thhe snapshot
    """
    return string.split("/")[-1]



def sun( angle ):
    """
    return the azimuth and altitude components whn given a 0-180 degree arc
    """
    az = 0 if angle <= 90 else 180
    al = angle if angle <= 90 else 180 - angle
    return (az, al)


# Set 360 pano mode
panomode = True
# Load the default skeleton config file
|config = json.load(open("skel.json", "r"))

# Other config stuff
lapse360folder = "/minecraft/spin-o-lapse"
chunky = "/minecraft/ChunkyLauncher.jar"
spp = 20
# Coordinates
coords = ("-248", "127", "370")

# Get the list of snapshots fom the filesystem
#snapshotsinitial = sorted(glob.glob("/minecraft/worlddisk*/.zfs/snapshot/2015*000?"), key=customsorter)
snapshotsinitialunchecked = sorted(glob.glob("/minecraft/worlddisk*/.zfs/snapshot/2015????00??"), key=customsorter)

# Filter only ones that have a level.dat (sometimes the snapshots gets the
# server mid save
snapshotsinitial = [snap for snap in snapshotsinitialunchecked if os.path.exists(snap + "/level.dat")]
#snapshotsinitial = snapshotsinitial[-6480:]

num = 360
snapshotsdistributed = [snapshotsinitial[int(math.floor(deg/float(num) * len(snapshotsinitial)))] for deg in xrange(num)]
snapshots = [snapshotsdistributed[0]] * 180 + snapshotsdistributed + [snapshotsdistributed[-1]] * 180
#snapshots = snapshots[0:20]




distance = 90

# Calculate the current chunk based on given coods
currentchunk = [int(coords[0]) // 16, int(coords[2]) // 16]
print currentchunk

chunkradius =  24

# Generate the list of chunks to load based on chunkradius
chunklist = [[x, y] for x in xrange(currentchunk[0] - chunkradius, currentchunk[0] + chunkradius + 1)
             for y in xrange(currentchunk[1] - chunkradius, currentchunk[1] + chunkradius + 1)]
chunklist = [[c[0], c[1]] for c in chunklist if ((c[0] - currentchunk[0])** 2 + (c[1] - currentchunk[1]) ** 2) <= chunkradius ** 2]

# print chunklist

# Set the chunklist for Chunky
config["chunkList"] = chunklist

config["sppTarget"] = spp

# Set pano stuff
if panomode:
    config["height"] = 2160
    config["width"] = 4320

    config["camera"]["projectionMode"] = "PANORAMIC"
    config["camera"]["fov"] = 180
    pitch = math.radians(0)
    fps="12"
else:
    config["camera"]["orientation"]["pitch"] = pitch - math.radians(90)
    pitch = math.radians(50)
    fps="24"

# Name is pased on the coordinates to keep everything separate
coordstext = "x" + coords[0] + "y" + coords[1] + "z" + coords[2]

# Set the camera to the sign coordinate
# config["camera"]["position"]["x"] = int(coords[0])
# config["camera"]["position"]["y"] = coords[1]
# config["camera"]["position"]["z"] = int(coords[2])

# Create the folder for all the files
folder = lapse360folder + "/" + coordstext
if not os.path.exists(folder):
    os.makedirs(folder)

# How many snapshots are there?
numsnapshots = len(snapshots)
# We'll need to keep track of which snapshot is which number
snapshotenum = enumerate(snapshots)

# Generate all the frames!
for snap in snapshotenum:
    # Name it meaningfully
    name = snap[1].split("/")[-1] + "." + coordstext + "." + str(snap[0]).rjust(5, "0")
    # Start at a 45 angle cuz it looks cool
    angle = snap[0] + 45
    config["name"] = name
    config["world"]["path"] = snap[1]
    # Set the coords so they rotate around the coords given using magic, I mean
    # math
    config["camera"]["orientation"]["yaw"] = math.radians(angle)
    config["camera"]["position"]["x"] = int(coords[0]) + math.cos(math.radians(angle)) * math.cos(pitch) * distance
    config["camera"]["position"]["y"] = int(coords[1]) + math.sin(pitch) * distance
    config["camera"]["position"]["z"] = int(coords[2]) - math.sin(math.radians(angle)) * math.cos(pitch) * distance
    sunangle = float(snap[0]) / numsnapshots * 180
    az, al = sun(sunangle)
    config["sun"]["azimuth"] = math.radians(az)
    config["sun"]["altitude"] = math.radians(al)
    # I want to know if it'll finish befor the heat death of the universe, get a
    # start time
    start = time.time()
    # write the scene file
    json.dump(config, open(folder + "/" +  name + ".json", "w"))
    # run chunky with the scene file on the snapshot
    command = "cgexec -g cpu:overviewer java -jar " + chunky + " -scene-dir " + folder + "/" + " -render " + name
    subprocess.call(command, shell=True)
    # add the name of the frame to the png, for posterity and troubleshooting
    subprocess.call("convert " + folder + "/" + name + "-"+str(spp)+".png -gravity southeast -stroke '#000C' -strokewidth 2 -annotate 0 \"" + name + "\" -stroke  none -fill white -annotate 0 \"" + name + "\" " + folder + "/" + name + "-annotated.png", shell=True)
    # cleanup
    for f in glob.glob(folder + "/" + name + ".*"): os.remove(f)
    os.remove(folder + "/" + name + "-"+ str(spp) + ".png")
    # is the universe over?
    stop = time.time()
    elapsed = stop - start
    # tell me how muc more coffee I have to dring until it's done
    print str(snap[0]) + " " + str(100.0 * (snap[0] + 1)/ numsnapshots) + " Hours left: " + str(elapsed * (numsnapshots - snap[0] + 1)/60/60)

# Make a video with all the frames
ffmpegcommand = "ffmpeg -y -framerate " + fps + " -pattern_type glob -i \"" + folder + "/" + "*.png\" -c:v libx264 -pix_fmt yuv420p " + folder + "/" + coordstext + ".mp4"
subprocess.call(ffmpegcommand, shell=True)
# send me a notification if I fell asleep
vanillabean.slack("Done spin-o-lapse " + folder)

# Add the 360 youtube metadata to the file
if panomode:

    metadatacommand = "python /minecraft/360VideosMetadata.py -i " + folder + "/" + coordstext + ".mp4 " + folder + "/" coordstext + "-meta.mp4"
    subprocess.call(metadatacommand, shell=True)
