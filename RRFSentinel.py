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
            logged[name]=1
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
        options, remainder = getopt.getopt(argv, '', ['help', 'count=', 'period='])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    for opt, arg in options:
        if opt == '--help':
            usage()
            sys.exit()
        elif opt in ('--count'):
            count = arg
        elif opt in ('--period'):
            period = arg

    print count, period

    # Boucle principale
    while(True):
        tmp = datetime.datetime.now()
        now = tmp.strftime('%H:%M:%S')
        hour = int(tmp.strftime('%H'))
        minute = int(now[3:-3])
        seconde = int(now[-2:])

        readlog()

        print links
        print ips
        print log

        print '-----'

        time.sleep(1000)

if __name__ == '__main__':
    try:
        main(sys.argv[1:])
    except KeyboardInterrupt:
        pass
