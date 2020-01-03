#!/bin/bash
sshpass -e rsync -aP -e "ssh -o StrictHostKeyChecking=no" $DATAFOLDER/backup/ $RSYNCNETUSERHOST:$SERVERNAME
