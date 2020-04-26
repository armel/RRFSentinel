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

    now = datetime.datetime.now()
    day = now.strftime('%Y-%m-%d')

    restart = False
    with open('/tmp/RRFSentinel.log') as f:
        for line in f:
            if day in line:
                restart = True
                break

    if restart is False:
        print '----------'
        print now.strftime('%Y-%m-%d')
        print '----------'
    else:
        print '-----'
        print 'Restart at ' + now.strftime('%H:%M:%S')
        print '-----'

    print 'RRFSentinel version ' + s.version
    print 'Salon: ' + s.salon
    print '-----'
    print 'Intempestif settings'
    print 'Plage: ' + str(s.intempestif_plage) + ' minutes'
    print 'Ban: ' + str(s.intempestif_ban) + ' minutes'
    print 'Déclenchements: ' + str(s.intempestif_tx)
    print 'Fair use: ' + str(s.intempestif_fair_use)
    print '-----'
    print 'Campeur settings'
    print 'Plage: ' + str(s.campeur_plage) + ' minutes'
    print 'Ban: ' + str(s.campeur_ban) + ' minutes'
    print 'Passage en émission: ' + str(s.campeur_tx)
    print 'Durée en émission: ' + str(s.campeur_bf)
    print 'Fair use: ' + str(s.campeur_fair_use)

    # Boucle principale
    while(True):
        now = datetime.datetime.now()

        plage_stop = now.strftime('%H:%M:%S')
        plage_start_intempestif = (now - datetime.timedelta(minutes = s.intempestif_plage)).strftime('%H:%M:%S')
        plage_start_campeur = (now - datetime.timedelta(minutes = s.campeur_plage)).strftime('%H:%M:%S')

        l.read_log()

        # Request HTTP datas
        try:
            r = requests.get(s.salon_list[s.salon]['url'], verify=False, timeout=1)
        except requests.exceptions.ConnectionError as errc:
            print ('Error Connecting:', errc)
        except requests.exceptions.Timeout as errt:
            print ('Timeout Error:', errt)

        try:
            rrf_data = r.json()

            #
            # Gestion des intempestifs
            #

            if 'porteuse' in rrf_data:
                for data in rrf_data['porteuse']:
                    s.porteuse[data[u'Indicatif'].encode('utf-8')] = [data[u'TX'], data[u'Date']]

            for p in s.porteuse:
                indicatif = p.strip()
                tx = s.porteuse[p][0]
                date = s.porteuse[p][1].split(', ')

                #print indicatif, tx, date

                if indicatif not in s.white_list:
                    count = 0
                    for h in date:
                        if h < plage_stop and h > plage_start_intempestif:
                            count += 1

                    if count >= s.intempestif_tx and indicatif in s.link_ip and indicatif not in s.ban_list:
                        try:
                            s.ban_count[indicatif] += 1
                        except KeyError:
                            s.ban_count[indicatif] = 1

                        if s.ban_count[indicatif] <= s.intempestif_fair_use:
                            ban_time = s.intempestif_ban
                        else:
                            if indicatif[-2:] == ' H':  # Si Hotspot
                                ban_time = int(tx) * (s.ban_count[indicatif] - s.intempestif_fair_use)
                            else:                       # Sinon...
                                ban_time = int(tx) * 2

                        ban_timestamp = (now + datetime.timedelta(minutes = ban_time))
                        ban_clock = ban_timestamp.strftime('%H:%M:%S')
                        ban_timestamp = time.mktime(ban_timestamp.timetuple())

                        s.ban_list[indicatif] = (ban_timestamp, s.link_ip[indicatif], 'INTEMPESTIF')

                        # Ban UDP
                        cmd = 'iptables -I INPUT -s ' + s.link_ip[indicatif] + ' -p udp --dport 5300 -j REJECT -m comment --comment \'RRFSentinel ' + indicatif + ' (INTEMPESTIF)\''
                        os.system(cmd)
                        print plage_stop + ' - ' + indicatif + ' - [' + ', '.join(date[-count:]) + ' @ ' + str(tx) + '] - ' + str(s.ban_count[indicatif]) + ' - ' + str(ban_time) + ' - ' + ban_clock + ' >> ' + cmd

                        # Ban TCP
                        cmd = 'iptables -I INPUT -s ' + s.link_ip[indicatif] + ' -p tcp --dport 5300 -j REJECT -m comment --comment \'RRFSentinel ' + indicatif + ' (INTEMPESTIF)\''
                        os.system(cmd)
                        print plage_stop + ' - ' + indicatif + ' - [' + ', '.join(date[-count:]) + ' @ ' + str(tx) + '] - ' + str(s.ban_count[indicatif]) + ' - ' + str(ban_time) + ' - ' + ban_clock + ' >> ' + cmd

            #
            # Gestion des campeurs
            #

            if 'all' in rrf_data:
                for data in rrf_data['all']:
                    indicatif = data[u'Indicatif'].encode('utf-8')

                    if l.convert_time_to_second(data[u'Durée']) >= s.campeur_bf:
                        bf = 0
                        tx = 0
                        h = data['Heure'].split(', ')
                        c = data['Chrono'].split(', ')
                        for t in xrange(len(h)):
                            if h[t] >= plage_start_campeur and h[t] < plage_stop:
                                tx += 1
                                bf += l.convert_time_to_second(c[t])
                                #print data[u'Indicatif'].encode('utf-8'), h[t], c[t], tx, bf, l.convert_second_to_time(bf)
                        if tx >= 10 and bf >= 360:
                            ban_timestamp = (now + datetime.timedelta(minutes = s.campeur_ban))
                            ban_clock = ban_timestamp.strftime('%H:%M:%S')
                            ban_timestamp = time.mktime(ban_timestamp.timetuple())

                            s.ban_list[indicatif] = (ban_timestamp, s.link_ip[indicatif], 'CAMPEUR')

                            # Ban UDP
                            cmd = 'iptables -I INPUT -s ' + s.link_ip[indicatif] + ' -p udp --dport 5300 -j REJECT -m comment --comment \'RRFSentinel ' + indicatif + ' (CAMPEUR)\''
                            os.system(cmd)
                            print plage_stop + ' - ' + indicatif + ' - [' + str(bf) + ' @ ' + str(tx) + '] - ' + str(s.campeur_ban) + ' - ' + ban_clock + ' >> ' + cmd

                            # Ban TCP
                            cmd = 'iptables -I INPUT -s ' + s.link_ip[indicatif] + ' -p tcp --dport 5300 -j REJECT -m comment --comment \'RRFSentinel ' + indicatif + ' (CAMPEUR)\''
                            os.system(cmd)
                            print plage_stop + ' - ' + indicatif + ' - [' + str(bf) + ' @ ' + str(tx) + '] - ' + str(s.campeur_ban) + ' - ' + ban_clock + ' >> ' + cmd

                    else:
                        break

        except:
            pass

        # Unban check
        unban_list = {}

        for b in s.ban_list:
            if time.mktime(now.timetuple()) > s.ban_list[b][0]:
                unban_list[b] = (s.ban_list[b][0], s.ban_list[b][1], s.ban_list[b][2])

        if unban_list:
            for b in unban_list:
                # Unban current reflector IP
                cmd = 'iptables -D INPUT -s ' + s.link_ip[b] + ' -p udp --dport 5300 -j REJECT -m comment --comment \'RRFSentinel ' + b + ' (' + unban_list[b][2] + ')\''
                os.system(cmd)
                print plage_stop + ' - ' + b + ' << ' + cmd

                cmd = 'iptables -D INPUT -s ' + s.link_ip[b] + ' -p tcp --dport 5300 -j REJECT -m comment --comment \'RRFSentinel ' + b + ' (' + unban_list[b][2] + ')\''
                os.system(cmd)
                print plage_stop + ' - ' + b + ' << ' + cmd

                # Unban old reflextor IP (at ban time... by security)
                cmd = 'iptables -D INPUT -s ' + unban_list[b][1] + ' -p udp --dport 5300 -j REJECT -m comment --comment \'RRFSentinel ' + b + ' (' + unban_list[b][2] + ')\''
                os.system(cmd)
                print plage_stop + ' - ' + b + ' << ' + cmd

                cmd = 'iptables -D INPUT -s ' + unban_list[b][1] + ' -p tcp --dport 5300 -j REJECT -m comment --comment \'RRFSentinel ' + b + ' (' + unban_list[b][2] + ')\''
                os.system(cmd)
                print plage_stop + ' - ' + b + ' << ' + cmd

                del s.ban_list[b]

        # If midnight
        if now.strftime('%H:%M') == '00:00':
            print '----------'
            print now.strftime('%Y-%m-%d')
            print '----------'
            # Waiting during RRFTracker init...
            s.porteuse.clear()
            time.sleep(60)

        # If time < 06:00am, fair use only !
        if now.strftime('%H:%M') < s.fair_use_time:
            # Reset ban_count
            s.ban_count.clear()

        time.sleep(2)
        sys.stdout.flush()

if __name__ == '__main__':
    try:
        main(sys.argv[1:])
    except KeyboardInterrupt:
        pass
