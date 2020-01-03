#!/bin/bash


BASEDIR="/minecraft"
LOG="$DATAFOLDER/logs/$1.log"
STATE="/tmp"

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
