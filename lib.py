#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
RRFSentinel
Learn more about RRF on https://f5nlg.wordpress.com
73 & 88 de F4HWN Armel
'''

import settings as s

import datetime
import time
import os
import sys
import requests
import socket

# Detection du serveur
def hostname_init():
    hostname = socket.gethostname()
    if hostname == 'rrf.f5nlg.ovh':
        s.serveur = 1
    elif hostname == 'rrf2.f5nlg.ovh':
        s.serveur = 2
    elif hostname == 'rrf3.f5nlg.ovh':
        s.serveur = 3
    else:
        exit()

# Recuperation des nodes
def read_log():
    nodes = ''

    # Requete HTTP vers le flux json de l'API fournie par F1EVM
    try:
        r = requests.get(s.nodes_json, verify=False, timeout=5)
    except:
        pass

    # Controle de la validité du flux json
    try:
        nodes = r.json()
    except:
        pass

    # Si le flux json est valide
    if nodes != '':
        s.link_ip.clear()
        for node in nodes['nodes']:
            if node[0] == s.serveur:
                s.link_ip[node[2].strip()] = node[3]
    '''
    # Sinon, on utilise la methode traditionnelle en lisant le log de svxreflector
    else:
        with open(s.nodes_file) as f:
            for line in f:
                if 'Login' in line:
                    element = line.split(':')
                    s.link_ip[element[3].strip()] = element[4][15:]
    '''

# Convert time to second
def convert_time_to_second(time):
    if len(time) > 5:
        format = [3600, 60, 1]
    else:
        format = [60, 1]        
    
    return sum([a * b for a, b in zip(format, list(map(int, time.split(':'))))])

# Add iptable
def add_iptable(ip, port, indicatif, type, ban_stop, ban_comment):
    with open(s.path_log, 'a+') as f:
        # udp
        cmd = 'sudo iptables -I INPUT -s ' + ip + ' -p udp --dport ' + str(port) + ' -j REJECT -m comment --comment \'RRFSentinel - ' + type + ' - ' + indicatif + ' - ' + ban_stop + '\''
        try:
            os.system(cmd)
        except:
            pass
        f.write(datetime.datetime.now().strftime('%H:%M:%S %d-%m-%Y') + ban_comment + ' >> ' + cmd + '\n')

        # tcp
        cmd = 'sudo iptables -I INPUT -s ' + ip + ' -p tcp --dport ' + str(port) + ' -j REJECT -m comment --comment \'RRFSentinel - ' + type + ' - ' + indicatif + ' - ' + ban_stop + '\''
        try:
            os.system(cmd)
        except:
            pass
        f.write(datetime.datetime.now().strftime('%H:%M:%S %d-%m-%Y') + ban_comment + ' >> ' + cmd + '\n')
    return True

# Del iptable
def del_iptable(ip, port, indicatif, type, ban_stop):
    with open(s.path_log, 'a') as f:
        # udp
        cmd = 'sudo iptables -D INPUT -s ' + ip + ' -p udp --dport ' + str(port) + ' -j REJECT -m comment --comment \'RRFSentinel - ' + type + ' - ' + indicatif  + ' - ' + ban_stop + '\''
        try:
            os.system(cmd)
        except:
            pass        
        f.write(datetime.datetime.now().strftime('%H:%M:%S %d-%m-%Y') + ' << ' + cmd + '\n')
        # tcp
        cmd = 'sudo iptables -D INPUT -s ' + ip + ' -p tcp --dport ' + str(port) + ' -j REJECT -m comment --comment \'RRFSentinel - ' + type + ' - ' + indicatif  + ' - ' + ban_stop + '\''
        try:
            os.system(cmd)
        except:
            pass
        f.write(datetime.datetime.now().strftime('%H:%M:%S %d-%m-%Y') + ' << ' + cmd + '\n')
    return True
