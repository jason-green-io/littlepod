# littlepod

"The word vanilla, derived from the diminutive of the Spanish word vaina (vaina itself meaning sheath or pod), translates simply as "little pod"."

`littlepod` is a set of scripts, Python modules and config files that wrap vanilla minecraft. They are used in conjunction with Docker to create servers.

## spin-o-lapse.py

Chunky wrapper that auto generates chunky time lapses.

How it works.

The Barlynaland server uses the zfs file system which allows it to copy the entire world every 20 minutes without taking up an entire world's worth of space on disk. zfs snapshots only store the changes. So what? That means we can use chunky on any given world snapshot, like a slice in time. Do this to multiple slices and you have a time lapse!

Let's take it one step further. Chunky renders using a camera set at one spot. Let's move the camera a bit, in a circle, for every snapshot from above. When you put them all together, you're rotating around a spot as the time lapse happens.

Kick it up a notch. Chunky allows you to render using a special 360 camera that captures everything around you. Combine this with tools from Google and put it on YouTube and you have an immersive rotating view of your world as it moves through time.

One more thing. Let's make the sun rise and set to show the passage of time. Just because.

That's a spin-o-lapse
