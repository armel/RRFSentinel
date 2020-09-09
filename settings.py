#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
RRFSentinel
Learn more about RRF on https://f5nlg.wordpress.com
73 & 88 de F4HWN Armel
'''

'''
Intempestif

Sur une plage d'une durée de 5 minutes
Si le nombre de déclenchement est supérieur ou égale à 4
On ban pour 5 minutes

Campeur

Sur une plage d'une durée de 60 minutes
Si le nombre de passage en émission est supérieur ou égale à 30
Et que le temps d'émission est supérieur ou égale à 1800 secondes (30 minutes)
On ban pour 15 minutes
'''

# Version

version = '2.4.0'

# Variables par defaut

salon = 'RRF'                   # room a surveiller

tot_limit = 120                 # durée du tot en secondes (durée de passage en émission avant action...)
tot_ban = 30                    # durée de la quarantaine en secondes

intempestif_plage = 5           # durée de la plage de déclenchements en minutes
intempestif_ban = 5             # durée de la quarantaine en minutes
intempestif_tx = 4              # nombre max de déclenchements suspects 
intempestif_fair_use = 3        # nombre de ban avant application de la règle strict

campeur_plage = 60              # durée de la plage de déclenchements en minutes
campeur_ban = 15                # durée de la quarantaine en minutes
campeur_tx = 30                 # nombre max de passage en émission
campeur_bf = 1800               # nombre max de seconde en émission

fair_use_time = '06:00' # heure de ban avant application de la règle strict

path_log = '/tmp/RRFSentinel.log'
path_pid = '/tmp/RRFSentinel.pid'
path_json = '/var/www/RRFBlockIP/data/RRFSentinel.json'

salon_list = {
    'RRF': {
        'url': 'http://rrf.f5nlg.ovh:8080/RRFTracker/RRF-today/rrf.json',
    }
}

porteuse = {}
all = {}
white_list = ['F5ZIN-L', 'R.R.F', 'R.R.F_V2', 'RRF', 'RRF3']
ban_list = {}
ban_count_tot = {}
ban_count_intempestif = {}
ban_count_campeur = {}

nodes_json = 'http://rrf2.f5nlg.ovh:4440/nodes'
nodes_file = '/tmp/svxreflector.log'

# Variables globales

link_ip = dict()
serveur = 0

