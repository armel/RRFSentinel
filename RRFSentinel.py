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
        now = datetime.datetime.now()
        plage_stop = now.strftime('%H:%M:%S')
        plage_start = (now - datetime.timedelta(minutes = s.plage)).strftime('%H:%M:%S')

        l.readlog()

        print s.prov

        # Request HTTP datas
        try:
            r = requests.get(s.salon_list[s.salon]['url'], verify=False, timeout=1)
            page = r.content
        except requests.exceptions.ConnectionError as errc:
            print ('Error Connecting:', errc)
        except requests.exceptions.Timeout as errt:
            print ('Timeout Error:', errt)


        print plage_start, plage_stop

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
                        if h < plage_stop and h > plage_start:
                            count += 1

                    if count >= s.declenchement and indicatif in s.prov and indicatif not in ban_list:
                        print indicatif, count, horodatage[-count:]
                        print '>> iptables -I INPUT -s ' + indicatif + ' -j DROP'
                        print '>> iptables -I INPUT -s ' + s.prov[indicatif] + ' -j DROP'
                        s.ban_list[indicatif] = (now + datetime.timedelta(minutes = s.ban)).strftime('%H:%M:%S')

                start += 2
                if line[start] == '],':
                    break
                else:
                    start += 2

            unban_list = []
            for b in s.ban_list:
                print b, s.ban_list[b]
                if now.strftime('%H:%M:%S') > s.ban_list[b]:
                    unban_list.append(b)

            if unban_list:
                for b in unban_list:
                    print '<< iptables -D INPUT -s ' + s.prov[b] + ' -j DROP'
                    del s.ban_list[b]


            print '-----'

        time.sleep(10)

if __name__ == '__main__':
    try:
        main(sys.argv[1:])
    except KeyboardInterrupt:
        pass
