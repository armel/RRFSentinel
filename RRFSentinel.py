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
import json

def main(argv):

    now = datetime.datetime.now()
    l.hostname_init()

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
            print(('Error Connecting:', errc))
        except requests.exceptions.Timeout as errt:
            print(('Timeout Error:', errt))

        try:
            rrf_data = r.json()

            #
            # Gestion des intempestifs
            #

            if 'porteuse' in rrf_data:
                for data in rrf_data['porteuse']:
                    s.porteuse[data['Indicatif']] = [data['TX'], data['Date']]

            for p in s.porteuse:
                indicatif = p.strip()
                tx = s.porteuse[p][0]
                date = s.porteuse[p][1].split(', ')

                #print(indicatif, tx, date)

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
                            if indicatif[-2:] == ' H' or indicatif[-2:] == ' S':  # Si Hotspot
                                ban_time = int(tx) * (s.ban_count[indicatif] - s.intempestif_fair_use)
                            else:                       # Sinon...
                                ban_time = int(tx) * 2

                        ban_start = plage_stop
                        ban_timestamp = (now + datetime.timedelta(minutes = ban_time))
                        ban_stop = ban_timestamp.strftime('%H:%M:%S')
                        ban_timestamp = time.mktime(ban_timestamp.timetuple())

                        s.ban_list[indicatif] = (ban_timestamp, s.link_ip[indicatif], 'INTEMPESTIF', ban_stop, ban_start, str(ban_time) + 'm')
                
                        ban_comment = ' - [' + ', '.join(date[-count:]) + ' @ ' + str(tx) + '] - ' + str(s.ban_count[indicatif]) + ' - ' + str(ban_time)
                        l.add_iptable(s.link_ip[indicatif], '5300', indicatif, 'INTEMPESTIF', ban_stop, ban_comment)
    
            #
            # Gestion des campeurs
            #

            if 'all' in rrf_data:
                for data in rrf_data['all']:
                    indicatif = data['Indicatif']
                    if indicatif not in s.ban_list and l.convert_time_to_second(data['Durée']) >= s.campeur_bf:
                        bf = 0
                        tx = 0
                        h = data['Heure'].split(', ')
                        c = data['Chrono'].split(', ')
                        print('la')
                        for t in range(len(h)):
                            if h[t] >= plage_start_campeur and h[t] < plage_stop:
                                tx += 1
                                bf += l.convert_time_to_second(c[t])
                            print(data['Indicatif'], h[t], c[t], tx, bf, l.convert_second_to_time(bf))
                        if tx >= s.campeur_tx and bf >= s.campeur_bf:
                            ban_start = plage_stop
                            ban_timestamp = (now + datetime.timedelta(minutes = s.campeur_ban))
                            ban_stop = ban_timestamp.strftime('%H:%M:%S')
                            ban_timestamp = time.mktime(ban_timestamp.timetuple())

                            s.ban_list[indicatif] = (ban_timestamp, s.link_ip[indicatif], 'CAMPEUR', ban_stop, ban_start, str(ban_time) + 'm')

                            ban_comment = ' - [' + str(bf) + ' @ ' + str(tx) + '] - ' + str(s.campeur_ban)
                            l.add_iptable(s.link_ip[indicatif], '5300', indicatif, 'CAMPEUR', ban_stop, ban_comment)

                    else:
                        break

        except:
            pass

        # Unban check
        unban_list = {}

        for b in s.ban_list:
            if time.mktime(now.timetuple()) > s.ban_list[b][0]:
                unban_list[b] = (s.ban_list[b][0], s.ban_list[b][1], s.ban_list[b][2], s.ban_list[b][3])

        if unban_list:
            for b in unban_list:
                # Unban current reflector IP
                l.del_iptable(s.link_ip[b], '5300', b, unban_list[b][2], unban_list[b][3])

                # Unban old reflextor IP (at ban time... by security)
                l.del_iptable(unban_list[b][1], '5300', b, unban_list[b][2], unban_list[b][3])

                del s.ban_list[b]

        # Write json for RRFBlockIP

        rrf_json = []
        for b in s.ban_list:
            rrf_json.append({
                'Indicatif': b,
                'Début': s.ban_list[b][4],
                'Durée': s.ban_list[b][5],
                'Fin': s.ban_list[b][3]
            })    

        with open(s.path_json, 'w') as f:
            json.dump(rrf_json, f)

        # If midnight
        if now.strftime('%H:%M') == '00:00':
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
