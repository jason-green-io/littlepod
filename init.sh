#/bin/bash
mkdir -p $DATAFOLDER/logs
mkdir -p $DATAFOLDER/state

rm -f $DATAFOLDER/state/*.pid

/usr/bin/envsubst '$GMAILPASSWORD $GMAILUSER $MCVERSION $DATAFOLDER $WEBDATA' < /minecraft/monitrc.envsubst > /minecraft/.monitrc
chmod 0700 /minecraft/.monitrc

/usr/bin/monit

tail -f /dev/null
