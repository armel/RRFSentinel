#!/usr/bin/env python2
# -*- coding: utf-8 -*-

'''
RRFSentinel
Learn more about RRF on https://f5nlg.wordpress.com
73 & 88 de F4HWN Armel
'''

import settings as s

# Usage
def usage():
    print 'Usage: RRFSentinel.py [options ...]'
    print
    print '--help                           cet aide'
    print
    print 'Parametrages:'
    print 
    print '  --salon            nom         nom du salon à surveiller: RRF ou RRF_V1'
    print '  --declenchement    nombre      nombre de déclenchements intempestifs'
    print '  --plage            nombre      durée de la plage, en minutes'
    print '  --ban              nombre      durée de la quarantaine, en minutes'
    print '  --faire-use        nombre      nombre de ban avant application de la règle strict'
    print
    print '88 & 73 from F4HWN Armel'


# lecture du svxreflector.log
def read_log():
    with open('/tmp/svxreflector.log') as f:
        for line in f:
            if 'Login' in line:
                element = line.split(':')
                s.link_ip[element[3].strip()] = element[4][15:]
