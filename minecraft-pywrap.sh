#!/bin/bash
BASEDIR="/minecraft"
LOG="$BASEDIR/host/otherdata/logs/$1.log"
case "$2" in
    start)
	echo "$(date) Started" >> $LOG
	"$BASEDIR/$1" >> $LOG 2>&1 &
	echo $! > "$BASEDIR/$1.pid"
	;;
    stop)
	echo "$(date) Stopped" >> $LOG
	kill $(<"$BASEDIR/$1.pid")
	;;
esac
