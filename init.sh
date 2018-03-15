#/bin/bash
mkdir -p $OTHERDATA

/usr/bin/envsubst '$GMAILPASSWORD $GMAILUSER'< /minecraft/monitrc.envsubst > /minecraft/.monitrc
chmod 0700 /minecraft/.monitrc

/usr/bin/monit

crontab /minecraft/crontab.txt

/bin/bash
