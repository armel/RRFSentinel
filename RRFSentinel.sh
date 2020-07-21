#!/bin/sh

PATH_SCRIPT='/opt/RRFSentinel/RRFSentinel.py'
PATH_PID='/tmp'

case "$1" in
    start)
        echo "Starting RRFSentinel"
        nohup python3 $PATH_SCRIPT > /dev/null 2>&1 & echo $! > $PATH_PID/RRFSentinel.pid
        ;;
    stop) 
        echo "Stopping RRFSentinel"
        kill `cat $PATH_PID/RRFSentinel.pid`
        ;;
    esac