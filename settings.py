#!/usr/bin/env python3
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

declenchement = 5	# nombre max de déclenchements suspects 
plage = 1			# durée de la plage de déclenchements en minutes
ban = 1				# durée de la quarantaine en minutes
salon = 'RRF'		# room a surveiller

salon_list = {
    'RRF': {
        'url': 'http://rrf.f5nlg.ovh:8080/RRFTracker/RRF-today/rrf.json',
    },
    'RRF_V1': {
        'url': 'http://rrf.f5nlg.ovh:8080/RRFTracker/RRF_V1-today/rrf.json',
    },
    'INTERNATIONAL': {
        'url': 'http://rrf.f5nlg.ovh:8080/RRFTracker/INTERNATIONAL-today/rrf.json',
    }
}

white_list = ['F5ZIN-L', 'R.R.F', 'R.R.F_V2', 'RRF', 'RRF3']

links = list()
ips = list()
log = list()
bip = dict()
prov = dict()
logged = dict()