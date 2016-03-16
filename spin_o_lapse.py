import json
import sys
import math
import glob
import os
import subprocess
import time


def customsorter(snap):
    """
    sort on the name of the snapshot
    """
    return snap[0].split("@")[-1]


def get_snaps():
    
    
    snaps = subprocess.check_output("sudo zfs list -t snapshot", shell=True).split("\n")
    snaps.remove("")
    snaps = [[x.split()[0], x.split()[4]] for x in snaps]
    snaps.remove(["NAME", "MOUNTPOINT"])
    return sorted(snaps, key=customsorter)



def sun(angle):
    """
    return the azimuth and altitude components whn given a 0-180 degree arc
    """
    az = 0 if angle <= 90 else 180
    al = angle if angle <= 90 else 180 - angle
    return (az, al)



if __name__ == "__main__":
    # Other config stuff
    lapse360folder = "/Volumes/TheBigOne/greener/minecraft/spin-o-lapse"
    chunky = "/Volumes/TheBigOne/greener/minecraft/ChunkyLauncher.jar"
    java = "/Applications/Minecraft.app/Contents/runtime/jre-x64/1.8.0_60/bin/java"
    # coords = ("-256", "128", "256")
    res = sys.argv[1].split("x")
    print res
    spp = int(sys.argv[2])
    coords = tuple(sys.argv[3:6])
    coordstext = "x" + coords[0] + "y" + coords[1] + "z" + coords[2]

    fps = "12"
    print spp, coords
    # Set 360 pano mode
    panomode = True

    # Spin?
    spin = False
    # spp = 20 
    # Coordinates

    # Create the folder for all the files
    folder = lapse360folder + "/" + coordstext
    if os.path.exists(folder):
        #os.makedirs(folder)

        # Load the default skeleton config file
        config = json.load(open("skel.json", "r"))

        # use 0 if you want everything
        startdate = 0
        stopdate = 201602262000
        distance = 90
        initialangle = 45


        # Set pano stuff
        if panomode:
            config["height"] = int(res[1])
            config["width"] = int(res[0])
            config["camera"]["orientation"]["pitch"] = math.radians(-90)

            config["camera"]["projectionMode"] = "PANORAMIC"
            config["camera"]["fov"] = 180
        else:
            pitch = math.radians(50)
            config["camera"]["orientation"]["pitch"] = pitch - math.radians(90)
            fps = "24"

        # set coords if we're not spinning
        if not spin:
            angle = initialangle
            config["camera"]["orientation"]["yaw"] = math.radians(angle)
            config["camera"]["position"]["x"] = int(coords[0])
            config["camera"]["position"]["y"] = int(coords[1])
            config["camera"]["position"]["z"] = int(coords[2])

        # Get the list of snapshots fom the filesystem
        # snapshotsinitial = sorted(glob.glob("/minecraft/worlddisk*/.zfs/snapshot/2015*000?"), key=customsorter)
        snapshotsinitial = [snap for snap in get_snaps() if int(customsorter(snap)) >= startdate and int(customsorter(snap)) <= stopdate]



        num = 360 - 48
        snapshotsdistributed = [snapshotsinitial[int(math.floor(deg/float(num) * len(snapshotsinitial)))] for deg in xrange(num)]
        
        snapshots = [snapshotsdistributed[0]] * 24 + snapshotsdistributed + [snapshotsdistributed[-1]] * 24
        
        #snapshots = snapshots[106:107]
        
        print snapshots[0], snapshots[-1]

        # Calculate the current chunk based on given coods
        currentchunk = [int(coords[0]) // 16, int(coords[2]) // 16]
        print currentchunk

        chunkradius =  24

        # Generate the list of chunks to load based on chunkradius
        chunklist = [[x, y] for x in xrange(currentchunk[0] - chunkradius, currentchunk[0] + chunkradius + 1)
                     for y in xrange(currentchunk[1] - chunkradius, currentchunk[1] + chunkradius + 1)]
        chunklist = [[c[0], c[1]] for c in chunklist if ((c[0] - currentchunk[0])** 2 + (c[1] - currentchunk[1]) ** 2) <= chunkradius ** 2]

        # Set the chunklist for Chunky
        config["chunkList"] = chunklist

        config["sppTarget"] = spp


        # Name is pased on the coordinates to keep everything separate


        # How many snapshots are there?
        numsnapshots = len(snapshots)

        # We'll need to keep track of which snapshot is which number
        snapshotenum = enumerate(snapshots)

        # Generate all the frames!
        redo = [170,187,163,226,224,114,243,102,260,97]
        finalsnaps = list(snapshotenum)
        finalsnaps = [finalsnaps[x] for x in redo]
        for snap in finalsnaps:
            # Name it meaningfully
            name = snap[1][0].split("@")[-1] + "." + coordstext + "." + str(snap[0]).rjust(5, "0")
            config["name"] = name
            config["world"]["path"] = snap[1][1]
            # Set the coords so they rotate around the coords given using magic, I mean
            # math
            if spin:
                # Start at a 45 angle cuz it looks cool
                angle = snap[1][1] + initialangle
                config["camera"]["orientation"]["yaw"] = math.radians(angle)
                config["camera"]["position"]["x"] = int(coords[0]) + math.cos(math.radians(angle)) * math.cos(pitch) * distance
                config["camera"]["position"]["y"] = int(coords[1]) + math.sin(pitch) * distance
                config["camera"]["position"]["z"] = int(coords[2]) - math.sin(math.radians(angle)) * math.cos(pitch) * distance
            sunangle = 45 + (float(snap[0]) / numsnapshots * 90)
            az, al = sun(sunangle)
            config["sun"]["azimuth"] = math.radians(az)
            config["sun"]["altitude"] = math.radians(al)
            # I want to know if it'll finish befor the heat death of the universe, get a
            # start time
            start = time.time()
            # write the scene file
            json.dump(config, open(folder + "/" +  name + ".json", "w"))

            subprocess.call("sudo zfs mount " + snap[1][0], shell=True)
            # run chunky with the scene file on the snapshot
            command = java + " -jar " + chunky + " -scene-dir " + folder + "/" + " -render " + name
            subprocess.call(command, shell=True)
            # add the name of the frame to the png, for posterity and troubleshooting
            
            subprocess.call("sudo zfs unmount " + snap[1][0], shell=True)
            subprocess.call("convert " + folder + "/" + name + "-" + str(spp) + ".png -gravity southeast -stroke '#000C' -strokewidth 2 -annotate 0 \"" + name + "\" -stroke  none -fill white -annotate 0 \"" + name + "\" " + folder + "/" + name + "-" + str(spp) + "-annotated.png", shell=True)
            # cleanup
            for f in glob.glob(folder + "/" + name + "*.dump"): os.remove(f)
            try:
                os.remove(folder + "/" + name + "-"+ str(spp) + ".png")
            except:
                pass
            # is the universe over?
            stop = time.time()
            elapsed = stop - start
            # tell me how muc more coffee I have to dring until it's done
            print str(snap[0]) + " " + str(100.0 * (snap[0] + 1)/ numsnapshots) + " Hours left: " + str(elapsed * (numsnapshots - snap[0] + 1)/60/60)
    else:
        files = glob.glob(folder + "/*.json")
        filesenum = enumerate(files)
        numfiles = len(files)
        for f in filesenum:
            start = time.time()
            with open(f[1], "r") as scenefile:
                scenefilejson = json.load(scenefile)
            scenefilejson["sppTarget"] = spp
            json.dump(scenefilejson, open(f[1], "w+"))
            name = f[1].split("/")[-1].rsplit(".", 1)[0]
            command = java + " -jar " + chunky + " --verbose -scene-dir " + folder + "/" + " -render " + name
            subprocess.call(command, shell=True)
            subprocess.call("convert " + folder + "/" + name + "-" + str(spp) + ".png -gravity southeast -stroke '#000C' -strokewidth 2 -annotate 0 \"" + name + "\" -stroke  none -fill white -annotate 0 \"" + name + "\" " + folder + "/" + name + "-" + str(spp) + "-annotated.png", shell=True)
            stop = time.time()
            elapsed = stop - start
            # tell me how much more coffee I have to dring until it's done
            print f[1] + " " + str(100.0 * (f[0] + 1)/ numfiles) + " Hours left: " + str(elapsed * (numfiles - f[0] + 1)/60/60)


    # Make a video with all the frames
    ffmpegcommand = "ffmpeg -y -framerate " + fps + " -pattern_type glob -i \"" + folder + "/*" + str(spp) + "-annotated.png\" -c:v libx264 -pix_fmt yuv420p " + folder + "/" + coordstext + ".mp4"
    subprocess.call(ffmpegcommand, shell=True)
    # send me a notification if I fell asleep

    # Add the 360 youtube metadata to the file
    if panomode:

        metadatacommand = "python /Volumes/TheBigOne/greener/minecraft/spatial-media/spatialmedia -i " + folder + "/" + coordstext + ".mp4 " + folder + "/" + coordstext + "-meta.mp4"
        subprocess.call(metadatacommand, shell=True)
