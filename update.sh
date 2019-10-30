#!/bin/bash

if [[ $# -eq 0 ]] ; then
    echo -e "Didn't provide version"
    exit 1
fi

export MCVERSION=$1
echo "Generating new .monitrc file"
/usr/bin/envsubst '$WEBDATA $DATAFOLDER $GMAILPASSWORD $GMAILUSER $MCVERSION' < /minecraft/monitrc.envsubst > /minecraft/.monitrc
echo "QUitting monit"
monit quit

sleep 2
echo "Starting monit"
monit
sleep 2
echo "Starting $MCVERSION server"
monit restart commandblock
monit start chatterbox
