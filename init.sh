#/bin/bash
mkdir -p $DATAFOLDER/logs

rm -f /tmp/*.pid

/usr/bin/envsubst '$DATAFOLDER' < /littlepod/monitrc.envsubst > /etc/monitrc

chmod 0700 /etc/monitrc

/usr/bin/monit

tail -f /dev/null
