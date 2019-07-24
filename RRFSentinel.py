#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
RRFSentinel
Learn more about RRF on https://f5nlg.wordpress.com
73 & 88 de F4HWN Armel
'''

import settings as s
import lib as l

import requests
import datetime
import os
import time
import sys
import getopt

def main(argv):

    # Check and get arguments
    try:
        options, remainder = getopt.getopt(argv, '', ['help', 'declenchement=', 'plage=', 'ban='])
    except getopt.GetoptError:
        l.usage()
        sys.exit(2)
    for opt, arg in options:
        if opt == '--help':
            l.usage()
            sys.exit()
        elif opt in ('--declenchement'):
            s.declenchement = int(arg)
        elif opt in ('--plage'):
            s.plage = int(arg)
        elif opt in ('--ban'):
            s.ban = int(arg)

    # Boucle principale
    while(True):
        tmp_stop = datetime.datetime.now()
        tmp_start = datetime.datetime.now() - datetime.timedelta(minutes = s.plage)
        search_stop = tmp_stop.strftime('%H:%M:%S')
        search_start = tmp_start.strftime('%H:%M:%S')

        #l.readlog()
        #print prov
        #print '---------------'

        # Request HTTP datas
        try:
            r = requests.get('http://rrf.f5nlg.ovh:8080/RRFTracker/RRF-today/rrf.json', verify=False, timeout=10)
            page = r.content
        except requests.exceptions.ConnectionError as errc:
            print ('Error Connecting:', errc)
        except requests.exceptions.Timeout as errt:
            print ('Timeout Error:', errt)


        print search_stop, search_start

        line = page.split('\n')
        start = line.index('"porteuseExtended":')

        start += 4

        while(True):
            indicatif = line[start].strip()
            indicatif = indicatif[14:-2]
            start += 2
            horodatage = line[start].strip()
            horodatage = horodatage[9:-1]
            horodatage = horodatage.split(', ')

            count = 0
            for h in horodatage:
                if h < search_stop and h > search_start:
                    count += 1

            if count >= s.declenchement:
                print 'iptables -I INPUT -s ' + indicatif + ' -p udp --dport 5300 -j DROP'

            start += 2
            if line[start] == '],':
                break
            else:
                start += 2

        print '-----'

        time.sleep(15)

if __name__ == '__main__':
    try:
        main(sys.argv[1:])
    except KeyboardInterrupt:
        pass
