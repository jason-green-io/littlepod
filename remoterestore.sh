#!/bin/bash
sshpass -e rsync -aP -e "ssh -o StrictHostKeyChecking=no" $RSYNCNETUSERHOST:$SERVERNAME/ $DATAFOLDER/mc
