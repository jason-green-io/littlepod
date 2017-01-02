#!/bin/bash
case "$1" in
    start)
	
	/usr/sbin/nginx -p /minecraft/host/config -c nginx.conf
	;;
    stop)
	/usr/sbin/nginx -q
	;;
esac
