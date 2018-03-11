#!/bin/bash

envsubst < /minecraft/server.properties.envsubst > /minecraft/host/mcdata/server.properties
envsubst < /minecraft/monitrc.envsubst > /minecraft/.monitrc
