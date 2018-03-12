#/bin/bash
/usr/bin/envsubst < /minecraft/server.properties.envsubst > /minecraft/host/mcdata/server.properties

/usr/bin/envsubst '$GMAILPASSWORD $GMAILUSER'< /minecraft/monitrc.envsubst > /minecraft/.monitrc
chmod 0700 /minecraft/.monitrc
/usr/bin/monit

crontab /minecraft/crontab.txt

/bin/bash
