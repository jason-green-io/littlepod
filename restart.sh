#!/bin/bash
{
echo "say Server restarting in 10s"
sleep 10
echo stop 
} | ncat localhost 7777 2>&1 | tee -a $DATAFOLDER/logs/restart.log
 
