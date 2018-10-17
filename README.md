# littlepod

"The word vanilla, derived from the diminutive of the Spanish word vaina (vaina itself meaning sheath or pod), translates simply as "little pod"."

`littlepod` is a set of scripts, Python modules and config files that wrap vanilla minecraft. They are used in conjunction with Docker to create servers.

## commandblock.sh

Launches minecraft server, downloads the jar of the specified version in `mcversion`. Wraps it with a ncat coproc allowing to access the console and piping commands to it. 

## seapigeon.py

Writes out the player `.dat` files in json every time they change. Allows for a tool like `jq` to parse the data.

## turtlesin.py

Generates stats on activity based on the minecraft_server log files.

## pywrap.sh

A wrapper for the python moduels so that monit can monitor them.

## chatterbox.py

Discord connectivity and whitelist management based on roles.

## littlepod_utils.py

Helper functions.

## showandtellraw.py

Kinda markdown parser to `/tellraw` json text.

## copypaste.sh

Backup the world to a local folder or backup service.
