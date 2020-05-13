#!/usr/bin/env python3
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
def save_horodatage(horodatage, indicatif, ban_date, ban_time, ban_end):
    try:
        horodatage[indicatif].append((ban_date, ban_time, ban_end[:8]))
    except KeyError:
        horodatage[indicatif] = [(ban_date, ban_time, ban_end[:8])]

    return horodatage

# Usage
def usage():
    print('Usage: RRFTracker.py [options ...]')
    print()
    print('--help               this help')
    print()
    print('Search settings:')
    print('  --day              set search day YYYY-MM-DD (default=current day)')
    print()
    print('88 & 73 from F4HWN Armel')

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

    intempestif_stat = dict()
    intempestif_horodatage = dict()
    intempestif_total_link = 0
    intempestif_total_ban = 0
    intempestif_total_time = 0

    campeur_stat = dict()
    campeur_horodatage = dict()
    campeur_total_link = 0
    campeur_total_ban = 0
    campeur_total_time = 0

    find = False
    hr = 0

    # compute stats

    log_path = '/root/F4HWN/RRFSentinel/RRFSentinel.log'
    pid_path = '/root/F4HWN/RRFSentinel/RRFSentinel.pid'

    with open(log_path) as f:
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
                    if len(element) == 6:
                        if '<<' not in element[1]:
                            if 'udp --dport 5300' in element[5]:
                                intempestif_stat = save_stat(intempestif_stat, element[1], int(element[4]))
                                intempestif_horodatage = save_horodatage(intempestif_horodatage, element[1], element[0], int(element[4]), element[5])
                    elif len(element) == 5:
                        if '<<' not in element[1]:
                            if 'udp --dport 5300' in element[4]:
                                campeur_stat = save_stat(campeur_stat, element[1], int(element[3]))
                                campeur_horodatage = save_horodatage(campeur_horodatage, element[1], element[0], int(element[3]), element[4])

    # 
    # Intempestif
    #

    intempestif_stat = sorted(list(intempestif_stat.items()), key=lambda x: x[1][1])
    intempestif_stat.reverse()

    print('--------------------')
    print(color.GREEN + '>>> Intempestifs <<<' + color.END)

    for s in intempestif_stat:
        intempestif_total_link += 1
        is_ban = False
        print('--------------------')

        for t in intempestif_horodatage[s[0]]:
            tmp = (now - datetime.timedelta(minutes = t[1])).strftime('%H:%M:%S')
            if t[0] > tmp:
                is_ban = True
                break

        if day == now.strftime('%Y-%m-%d') and is_ban is True:
            print(color.RED + s[0] + ': Ban en cours !!!' + color.END)
        else:
            print(color.GREEN + s[0] + ':' + color.END)

        b = 1
        for t in intempestif_horodatage[s[0]]:
            print('\t-> Ban %02d' % b, end=' ')
            print('à', t[0] + ' pour ' + str(t[1]) + ' minutes' + ' (' + t[2] + ')')
            b += 1

        print('Total\t=>', end=' ')
        
        print('%02d' % s[1][0], end=' ')
        if s[1][0] > 1:
            print('bans, pour', end=' ')
        else:
            print('ban, pour', end=' ')
        print(s[1][1], end=' ')
        print('minutes')

        intempestif_total_ban += s[1][0]
        intempestif_total_time += s[1][1]

    print('--------------------')
    print(color.GREEN + 'Résumé de la journée:' + color.END)
    print('\t-> Nombre de links bannis: ' + str(intempestif_total_link))
    print('\t-> Nombre de bannissement: ' + str(intempestif_total_ban))
    print('\t-> Durée total: ' + str(intempestif_total_time) + ' minutes')

    # 
    # Campeur
    #

    campeur_stat = sorted(list(campeur_stat.items()), key=lambda x: x[1][1])
    campeur_stat.reverse()

    print('--------------------')
    print(color.GREEN + '>>>   Campeurs   <<<' + color.END)

    for s in campeur_stat:
        campeur_total_link += 1
        is_ban = False
        print('--------------------')

        for t in campeur_horodatage[s[0]]:
            tmp = (now - datetime.timedelta(minutes = t[1])).strftime('%H:%M:%S')
            if t[0] > tmp:
                is_ban = True
                break

        if day == now.strftime('%Y-%m-%d') and is_ban is True:
            print(color.RED + s[0] + ': Ban en cours !!!' + color.END)
        else:
            print(color.GREEN + s[0] + ':' + color.END)

        b = 1
        for t in campeur_horodatage[s[0]]:
            print('\t-> Ban %02d' % b, end=' ')
            print('à', t[0] + ' pour ' + str(t[1]) + ' minutes' + ' (' + t[2] + ')')
            b += 1

        print('Total\t=>', end=' ')
        
        print('%02d' % s[1][0], end=' ')
        if s[1][0] > 1:
            print('bans, pour', end=' ')
        else:
            print('ban, pour', end=' ')
        print(s[1][1], end=' ')
        print('minutes')

        campeur_total_ban += s[1][0]
        campeur_total_time += s[1][1]

    print('--------------------')
    print(color.GREEN + 'Résumé de la journée:' + color.END)
    print('\t-> Nombre de links bannis: ' + str(campeur_total_link))
    print('\t-> Nombre de bannissement: ' + str(campeur_total_ban))
    print('\t-> Durée total: ' + str(campeur_total_time) + ' minutes')

    #
    # check pid
    #

    print('--------------------')
    print(color.GREEN + 'Status:' + color.END)

    f = open(pid_path)
    tmp = f.readlines()
    pid = int(tmp[0].strip())

    if psutil.pid_exists(pid):
        print(color.GREEN + '\t-> Success - RRFSentinel with pid %d exists' % pid)
    else:
        print(color.RED + '\t-> Failure - RRFSentinel with pid %d does not exist' % pid)
    print(color.END)

if __name__ == '__main__':
    try:
        main(sys.argv[1:])
    except KeyboardInterrupt:
        pass