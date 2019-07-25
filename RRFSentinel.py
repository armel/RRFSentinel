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
        options, remainder = getopt.getopt(argv, '', ['help', 'declenchement=', 'plage=', 'ban=', 'salon='])
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
        elif opt in ('--salon'):
            if arg not in ['RRF', 'RRF_V1', 'INTERNATIONAL']:
                print 'Nom de salon inconnu (choisir parmi \'RRF\', \'RRF_V1\', ou \'INTERNATIONAL\')'
                sys.exit()
            s.salon = arg

    print 'Salon %s, déclenchement %d, plage %d minute, ban %d minutes' % (s.salon, s.declenchement, s.plage, s.ban)


    # Boucle principale
    while(True):
        tmp_stop = datetime.datetime.now()
        tmp_start = datetime.datetime.now() - datetime.timedelta(minutes = s.plage)
        search_stop = tmp_stop.strftime('%H:%M:%S')
        search_start = tmp_start.strftime('%H:%M:%S')

        l.readlog()
        print s.prov
        #print '---------------'

        # Request HTTP datas
        try:
            r = requests.get(s.salon_list[s.salon]['url'], verify=False, timeout=1)
            page = r.content
        except requests.exceptions.ConnectionError as errc:
            print ('Error Connecting:', errc)
        except requests.exceptions.Timeout as errt:
            print ('Timeout Error:', errt)


        print search_stop, search_start

        line = page.split('\n')
        start = line.index('"porteuseExtended":')

        if line[start + 2] != '],':

            start += 4

            while(True):
                indicatif = line[start].strip()
                indicatif = indicatif[14:-2]
                start += 2
                horodatage = line[start].strip()
                horodatage = horodatage[9:-1]
                horodatage = horodatage.split(', ')

                if indicatif not in s.white_list:
                    count = 0
                    for h in horodatage:
                        if h < search_stop and h > search_start:
                            count += 1

                    if count >= s.declenchement:
                        print indicatif, count, horodatage[-count:]
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
