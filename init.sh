#/bin/bash
mkdir -p $DATAFOLDER/logs

rm -f /tmp/*.pid

/usr/bin/envsubst '$GMAILPASSWORD $GMAILUSER' < /minecraft/monitrc.envsubst > /minecraft/.monitrc
chmod 0700 /minecraft/.monitrc

/usr/bin/monit
/usr/bin/monit reload


tail -f /dev/null
