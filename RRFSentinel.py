#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
RRFSentinel
Learn more about RRF on https://f5nlg.wordpress.com
73 & 88 de F4HWN Armel
'''

import requests
import datetime
import os
import time
import sys
import getopt

links = list()
ips = list()
log = list()
bip = dict()
prov = dict()
logged = dict()


def usage():
    return true

def fctSort(e):
    # Cette fonction renvoie le nom du link afin de trier la liste.
    n = e.split(':')
    return n[3].strip()

def readbip():
    # readbip lit le fichier BIP.txt pour alimentre le dictionnary bip
    f = open('/root/BIP.txt','r')
    for x in f:
      e = x.split(":")
      bip[e[0]] = e[1]
    f.close()

def writebip():
    # writebip sauvegarde le dictionnary bip dans BIP.txt.
    f = open('/root/BIP.txt','w')
    for n in bip:
      txt = n + ':' + bip[n] + ':\n'
      f.write(txt)
    f.close()

def writelog(txt):
    fl=open('/root/blockIP.log','a')
    fl.write(txt)
    fl.close()

def readlog():
    # lecture du svxreflector.log
    
    f = open('/tmp/svxreflector.log')
    i = 0
    for x in f:
        e = x.split(':')
        name = e[3].strip()
        if 'Login' in x:
            log.append(x)
            logged[name] = 1
        elif 'disconnected' in x:
            if 'Client' not in name:
                logged[name] = 0
    f.close()
    log.reverse()
    log.sort(key = fctSort)

    lastName = ''
    name = ''
    i = 0
    for x in log:
        e = x.split(':')
        name=e[3].strip()
        if name != lastName:
            prov[name] = e[4][15:]
            lastName=name
            i += 1
    readbip()
    for x in bip:
        if x not in prov:
            prov[x]='---.---.---.---'
    i = 0
    for key in sorted(prov.keys()) :
        links.append(key)
        ips.append(prov[key])
        i += 1

def main(argv):

    # Check and get arguments
    try:
        options, remainder = getopt.getopt(argv, '', ['help', 'limit=', 'period='])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    for opt, arg in options:
        if opt == '--help':
            usage()
            sys.exit()
        elif opt in ('--limit'):
            limit = int(arg)
        elif opt in ('--period'):
            period = int(arg)

    # Boucle principale
    while(True):
        tmp_stop = datetime.datetime.now()
        tmp_start = datetime.datetime.now() - datetime.timedelta(minutes = period)
        search_stop = tmp_stop.strftime('%H:%M:%S')
        search_start = tmp_start.strftime('%H:%M:%S')

        search_stop = '02:10:00'        
        search_start = '02:09:00'

        #readlog()
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

            if count >= limit:
                print 'iptables -I INPUT -s ' + indicatif + ' -p udp --dport 5300 -j DROP'

            print '-----'
            start += 2
            if line[start] == '],':
                break
            else:
                start += 2

        time.sleep(10)

if __name__ == '__main__':
    try:
        main(sys.argv[1:])
    except KeyboardInterrupt:
        pass
