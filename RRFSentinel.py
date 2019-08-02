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
        options, remainder = getopt.getopt(argv, '', ['help', 'salon=', 'declenchement=', 'plage=', 'ban=', 'fair-use='])
    except getopt.GetoptError:
        l.usage()
        sys.exit(2)
    for opt, arg in options:
        if opt == '--help':
            l.usage()
            sys.exit()
        elif opt in ('--salon'):
            if arg not in ['RRF', 'RRF_V1']:
                print 'Nom de salon inconnu (choisir parmi \'RRF\' ou \'RRF_V1\')'
                sys.exit()
            s.salon = arg
        elif opt in ('--declenchement'):
            s.declenchement = int(arg)
        elif opt in ('--plage'):
            s.plage = int(arg)
        elif opt in ('--ban'):
            s.ban = int(arg)
        elif opt in ('--fair-use'):
            s.fair_use = int(arg)

    print 'RRFSentinel version ' + s.version
    print 'Salon: ' + s.salon
    print 'Déclenchements: ' + str(s.declenchement)
    print 'Plage: ' + str(s.plage) + ' minutes'
    print 'Ban: ' + str(s.ban) + ' minutes'
    print 'Fair use: ' + str(s.fair_use)

    now = datetime.datetime.now()
    
    print '----------'
    print now.strftime('%Y-%m-%d')
    print '----------'

    # Boucle principale
    while(True):
        now = datetime.datetime.now()
        plage_stop = now.strftime('%H:%M:%S')
        plage_start = (now - datetime.timedelta(minutes = s.plage)).strftime('%H:%M:%S')

        l.read_log()

        #print s.link_ip

        # Request HTTP datas
        try:
            r = requests.get(s.salon_list[s.salon]['url'], verify=False, timeout=1)
            page = r.content
        except requests.exceptions.ConnectionError as errc:
            print ('Error Connecting:', errc)
        except requests.exceptions.Timeout as errt:
            print ('Timeout Error:', errt)


        #print plage_start, plage_stop

        start = None
        line = page.split('\n')

        try:
            start = line.index('"porteuseExtended":')
        except ValueError:
            print('Problème de lecture du fichier JSON')

        if start != None:

            if line[start + 2] != '],':

                start += 4

                while(True):
                    indicatif = line[start].strip()
                    indicatif = indicatif[14:-2]

                    start += 1
                    tx = line[start].strip()
                    tx = tx[6:-1]

                    start += 1
                    date = line[start].strip()
                    date = date[9:-1]
                    date = date.split(', ')

                    if indicatif not in s.white_list:
                        count = 0
                        for h in date:
                            if h < plage_stop and h > plage_start:
                                count += 1

                        if count >= s.declenchement and indicatif in s.link_ip and indicatif not in s.ban_list:
                            try:
                                s.ban_count[indicatif] += 1
                            except KeyError:
                                s.ban_count[indicatif] = 1

                            if s.ban_count[indicatif] <= s.fair_use:
                                ban_time = s.ban
                            else:
                                ban_time = int(tx)

                            s.ban_list[indicatif] = (now + datetime.timedelta(minutes = ban_time)).strftime('%H:%M:%S')

                            # Ban UDP
                            cmd = 'iptables -I INPUT -s ' + s.link_ip[indicatif] + ' -p udp --dport 5300 -j REJECT -m comment --comment RRFSentinel'
                            os.system(cmd)
                            print plage_stop + ' - ' + indicatif + ' - [' + ', '.join(date[-count:]) + '] - ' + str(s.ban_count[indicatif]) + ' - ' + str(ban_time) + ' - ' + s.ban_list[indicatif] + ' >> ' + cmd

                            # Ban TCP
                            cmd = 'iptables -I INPUT -s ' + s.link_ip[indicatif] + ' -p tcp --dport 5300 -j REJECT -m comment --comment RRFSentinel'
                            os.system(cmd)
                            print plage_stop + ' - ' + indicatif + ' - [' + ', '.join(date[-count:]) + '] - ' + str(s.ban_count[indicatif]) + ' - ' + str(ban_time) + ' - ' + s.ban_list[indicatif] + ' >> ' + cmd

                    start += 2
                    if line[start] == '],':
                        break
                    else:
                        start += 2

                unban_list = []

                for b in s.ban_list:
                    if now.strftime('%H:%M:%S') > s.ban_list[b] or now.strftime('%H:%M') == '00:00':
                        unban_list.append(b)

                if unban_list:
                    for b in unban_list:
                        cmd = 'iptables -D INPUT -s ' + s.link_ip[b] + ' -p udp --dport 5300 -j REJECT -m comment --comment RRFSentinel'
                        os.system(cmd)
                        print plage_stop + ' - ' + b + ' << ' + cmd
                        cmd = 'iptables -D INPUT -s ' + s.link_ip[b] + ' -p tcp --dport 5300 -j REJECT -m comment --comment RRFSentinel'
                        os.system(cmd)
                        print plage_stop + ' - ' + b + ' << ' + cmd

                        del s.ban_list[b]

        # If midnight
        if now.strftime('%H:%M') == '00:00':
            print '----------'
            print now.strftime('%Y-%m-%d')
            print '----------'
            # Waiting during RRFTracker init...
            time.sleep(60)

        # If time < 06:00am, fair use only !
        if now.strftime('%H:%M') < '06:00':
            # Reset ban_count
            s.ban_count.clear()
        
        time.sleep(2)

        sys.stdout.flush()

if __name__ == '__main__':
    try:
        main(sys.argv[1:])
    except KeyboardInterrupt:
        pass
