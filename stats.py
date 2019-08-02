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

# Ansi color
class color:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

# Save stats
def save_stat(stat, indicatif, ban_time):
    try:
        stat[indicatif][0] += 1
        stat[indicatif][1] += ban_time
    except KeyError:
        stat[indicatif] = [1, ban_time]

    return stat

# Save stats
def save_horodatage(horodatage, indicatif, ban_date, ban_time):
    try:
        horodatage[indicatif].append((ban_date, ban_time))
    except KeyError:
        horodatage[indicatif] = [(ban_date, ban_time)]

    return horodatage

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

    now = datetime.datetime.now()
    day = now.strftime('%Y-%m-%d')

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
    horodatage = dict()

    find = False
    hr = 0

    # compute stats

    total_link = 0
    total_ban = 0
    total_time = 0

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
                        horodatage = save_horodatage(horodatage, element[1], element[0], int(element[4]))


    stat = sorted(stat.items(), key=lambda x: x[1][1])
    stat.reverse()

    for s in stat:
        total_link += 1
        is_ban = False
        print '--------------------'

        for t in horodatage[s[0]]:
            tmp = (now - datetime.timedelta(minutes = t[1])).strftime('%H:%M:%S')
            if t[0] > tmp:
                is_ban = True
                break

        if day == now.strftime('%Y-%m-%d') and is_ban is True:
            print color.RED + s[0] + ': Ban en cours !!!' + color.END
        else:
            print color.GREEN + s[0] + ':' + color.END

        b = 1
        for t in horodatage[s[0]]:
            print '\t-> Ban %02d' % b,
            print 'à', t[0] + ' pour ' + str(t[1]) + ' minutes'
            b += 1

        print 'Total\t=>',
        
        print '%02d' % s[1][0],
        if s[1][0] > 1:
            print 'bans, pour',
        else:
            print 'ban, pour',
        print s[1][1],
        print 'minutes'

        total_ban += s[1][0]
        total_time += s[1][1]

    print '--------------------'
    print color.GREEN + 'Résumé de la journée:' + color.END
    print '\t-> Nombre de links bannis: ' + str(total_link)
    print '\t-> Nombre de bannissement: ' + str(total_ban)
    print '\t-> Durée total: ' + str(total_time) + ' minutes'


    print '--------------------'
    print color.GREEN + 'Status:' + color.END

    # check pid

    f = open('/tmp/RRFSentinel.pid')
    tmp = f.readlines()
    pid = int(tmp[0].strip())

    if psutil.pid_exists(pid):
        print color.GREEN + '\t-> Success - RRFSentinel with pid %d exists' % pid
    else:
        print color.RED + '\t-> Failure - RRFSentinel with pid %d does not exist' % pid
    print color.END

if __name__ == '__main__':
    try:
        main(sys.argv[1:])
    except KeyboardInterrupt:
        pass