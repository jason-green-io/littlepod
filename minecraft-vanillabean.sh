#!/bin/bash
if [[ ! -f /minecraft/vanillabean ]]; then
    mkfifo /minecraft/vanillabean

cat > vanillabean
