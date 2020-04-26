#!/bin/sh

PATH_SCRIPT='/root/F4HWN/RRFSentinel/RRFSentinel.py'
PATH_LOG='/root/F4HWN/RRFSentinel/'
PATH_PID='/root/F4HWN/RRFSentinel/'

case "$1" in
    start)
        echo "Starting RRFSentinel"
        nohup python $PATH_SCRIPT >> $PATH_LOG/RRFSentinel.log 2>&1 & echo $! > $PATH_PID/RRFSentinel.pid
        ;;
    stop) 
        echo "Stopping RRFSentinel"
        kill `cat $PATH_PID/RRFSentinel.pid`
        ;;
    esac