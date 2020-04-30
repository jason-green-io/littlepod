#!/bin/bash

curl -H "Content-Type: application/json" \
-X POST \
-d '{"username": "'"$MONIT_HOST"'", "content": "<@140194230168453120>'"$MONIT_PROGRAM_STATUS / $MONIT_SERVICE / $MONIT_EVENT / $MONIT_DESCRIPTION"'"}' $WEBHOOK
