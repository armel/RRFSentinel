#!/usr/bin/env python2
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
        options, remainder = getopt.getopt(argv, '', ['help', 'declenchement=', 'plage=', 'ban=', 'salon=', 'log-path='])
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
            if arg not in ['RRF', 'RRF_V1']:
                print 'Nom de salon inconnu (choisir parmi \'RRF\' ou \'RRF_V1\')'
                sys.exit()
            s.salon = arg
        elif opt in ('--log-path'):
            s.log_path = arg

    print 'Salon: ' + s.salon
    print 'Déclenchement: ' + str(s.declenchement)
    print 'Plage: ' + str(s.plage) + ' minute(s)'
    print 'Ban: ' + str(s.ban) + ' minute(s)'
    print 'Log: ' + s.log_path 
    
    # Boucle principale
    while(True):
        now = datetime.datetime.now()
        plage_stop = now.strftime('%H:%M:%S')
        plage_start = (now - datetime.timedelta(minutes = s.plage)).strftime('%H:%M:%S')

        l.readlog()

        #print s.prov

        # Request HTTP datas
        try:
            r = requests.get(s.salon_list[s.salon]['url'], verify=False, timeout=1)
            page = r.content
        except requests.exceptions.ConnectionError as errc:
            print ('Error Connecting:', errc)
        except requests.exceptions.Timeout as errt:
            print ('Timeout Error:', errt)


        #print plage_start, plage_stop

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

                    if count >= s.declenchement and indicatif in s.prov and indicatif not in s.ban_list:
                        #print indicatif, count, horodatage[-count:]
                        #print '>> iptables -I INPUT -s ' + indicatif + ' -j DROP'
                        cmd = 'iptables -I INPUT -s ' + s.prov[indicatif] + ' -j DROP'
                        os.system(cmd)
                        s.ban_list[indicatif] = (now + datetime.timedelta(minutes = s.ban)).strftime('%H:%M:%S')
                        print plage_stop + ' - ' + indicatif + ' [ ' + ', '.join(horodatage[-count:]) + '] >> ' + cmd

                start += 2
                if line[start] == '],':
                    break
                else:
                    start += 2

            unban_list = []

            with open(s.log_path +'/RRFSentinel_ban.log', 'w') as f:
                for b in s.ban_list:
                    print >> f, b, s.prov[b], s.ban_list[b]
                    #print b, s.ban_list[b]
                    if now.strftime('%H:%M:%S') > s.ban_list[b]:
                        unban_list.append(b)

            if unban_list:
                for b in unban_list:
                    cmd = 'iptables -D INPUT -s ' + s.prov[b] + ' -j DROP'
                    os.system(cmd)
                    print plage_stop + ' ' + b + ' << ' + cmd
                    del s.ban_list[b]

        sys.stdout.flush()
        time.sleep(2)

if __name__ == '__main__':
    try:
        main(sys.argv[1:])
    except KeyboardInterrupt:
        pass
