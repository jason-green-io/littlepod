#!/bin/bash
if [[ ! -f /minecraft/vanillabean ]]; then
    mkfifo /minecraft/vanillabean
fi
cat > vanillabean
