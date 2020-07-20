#!/bin/sh

PATH_SCRIPT='/opt/RRFSentinel/RRFSentinel.py'
PATH_LOG='/root'
PATH_PID='/root'

case "$1" in
    start)
        echo "Starting RRFSentinel"
        nohup python3 $PATH_SCRIPT >> $PATH_LOG/RRFSentinel.log 2>&1 & echo $! > $PATH_PID/RRFSentinel.pid
        ;;
    stop) 
        echo "Stopping RRFSentinel"
        kill `cat $PATH_PID/RRFSentinel.pid`
        ;;
    esac