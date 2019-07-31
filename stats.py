#!/usr/bin/env python2
# -*- coding: utf-8 -*-

'''
RRFSentinel
Learn more about RRF on https://f5nlg.wordpress.com
73 & 88 de F4HWN Armel
'''

import os
import sys
import getopt
import datetime
import time
import psutil

# Save stats
def save_stat(stat, indicatif, ban_time):
    try:
        stat[indicatif][0] += 1
        stat[indicatif][1] += ban_time
    except KeyError:
        stat[indicatif] = [1, ban_time]

    return stat

# Usage
def usage():
    print 'Usage: RRFTracker.py [options ...]'
    print
    print '--help               this help'
    print
    print 'Search settings:'
    print '  --day              set search day YYYY-MM-DD (default=current day)'
    print
    print '88 & 73 from F4HWN Armel'

def main(argv):

    tmp = datetime.datetime.now()
    day = tmp.strftime('%Y-%m-%d')

    # Check and get arguments
    try:
        options, remainder = getopt.getopt(argv, '', ['help', 'day='])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    for opt, arg in options:
        if opt == '--help':
            usage()
            sys.exit()
        elif opt in ('--day'):
            day = arg

    stat = dict()

    find = False
    hr = 0

    # check pid

    f = open('/tmp/RRFSentinel.pid')
    tmp = f.readlines()
    pid = int(tmp[0].strip())

    if psutil.pid_exists(pid):
        print 'Success - RRFSentinel with pid %d exists' % pid
    else:
        print 'Failure - RRFSentinel with pid %d does not exist' % pid

    # compute stats

    with open('/tmp/RRFSentinel.log') as f:
        for line in f:
            if day in line:
                find = True

            if find is True:
                if '----------' in line:
                    hr += 1
                    if hr == 2:
                        break

                if ' - ' in line:
                    element = line.split(' - ')
                    if '<<' not in element[1]:
                        stat = save_stat(stat, element[1], int(element[4]))

    stat = sorted(stat.items(), key=lambda x: x[1][1])
    stat.reverse()

    for s in stat:
        print s[0] + ':\t',
        print '%03d' % s[1][1],
        print ' minutes, pour ',
        print '%03d' % s[1][0],
        if s[1][0] > 1:
            print ' bans'
        else:
            print ' ban'


if __name__ == '__main__':
    try:
        main(sys.argv[1:])
    except KeyboardInterrupt:
        pass