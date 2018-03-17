#/bin/bash
mkdir -p $OTHERDATA/logs

/usr/bin/envsubst '$GMAILPASSWORD $GMAILUSER'< /minecraft/monitrc.envsubst > /minecraft/.monitrc
chmod 0700 /minecraft/.monitrc

/usr/bin/monit

/bin/bash
