#!/usr/bin/env python2
# -*- coding: utf-8 -*-

'''
RRFSentinel
Learn more about RRF on https://f5nlg.wordpress.com
73 & 88 de F4HWN Armel
'''

'''
Si le nombre de déclemenets et supérieur ou égale à 4
Sur une durée de 1 minute
On ban pour 15 minutes
'''

# Version

version = '0.0.6'

# Variables par defaut

salon = 'RRF'           # room a surveiller
declenchement = 3       # nombre max de déclenchements suspects 
plage = 5               # durée de la plage de déclenchements en minutes
ban = 5                 # durée de la quarantaine en minutes
fair_use = 3            # nombre de ban avant application de la règle strict

salon_list = {
    'RRF': {
        'url': 'http://rrf.f5nlg.ovh:8080/RRFTracker/RRF-today/rrf.json',
    },
    'RRF_V1': {
        'url': 'http://rrf.f5nlg.ovh:8080/RRFTracker/RRF_V1-today/rrf.json',
    },
}

white_list = ['F5ZIN-L', 'R.R.F', 'R.R.F_V2', 'RRF', 'RRF3']
ban_list = {}
ban_count = {}

# Variables globales

link_ip = dict()
