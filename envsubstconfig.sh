#!/bin/bash

envsubst < /minecraft/server.properties.envsubst > /minecraft/mcdata/server.properties
envsubst < /minecraft/monit.envsubst > /minecraft/.monitrc
