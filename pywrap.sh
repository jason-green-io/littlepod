#!/bin/bash


BASEDIR="/littlepod"
LOG="$DATAFOLDER/logs/$1.log"
STATE="/tmp"

$BASEDIR/alert.sh

export PYTHONIOENCODING="utf-8"
case "$2" in
    start)
	echo "$(date) Started" >> $LOG
	"$BASEDIR/$1" >> $LOG 2>&1 &
	echo $! > "$STATE/$1.pid"
	;;
    stop)
	echo "$(date) Stopped" >> $LOG
	kill $(<"$STATE/$1.pid")
	;;
esac
