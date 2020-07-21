#!/bin/sh

PATH_SCRIPT='/root/RRFSentinel/RRFSentinel.py'
PATH_LOG='/root'
PATH_PID='/root'

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