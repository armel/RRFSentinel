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

# lecture du svxreflector.log
def read_log():
    with open('/tmp/svxreflector.log') as f:
        for line in f:
            if 'Login' in line:
                element = line.split(':')
                s.link_ip[element[3].strip()] = element[4][15:]

# Convert time to second
def convert_time_to_second(time):
    if len(time) > 5:
        format = [3600, 60, 1]
    else:
        format = [60, 1]        
    
    return sum([a * b for a, b in zip(format, list(map(int, time.split(':'))))])

# Add iptable
def add_iptable(ip, port, indicatif, type, ban_clock, ban_comment):
    with open(s.path_log, 'a+') as f:
        # udp
        cmd = 'sudo iptables -I INPUT -s ' + ip + ' -p udp --dport ' + str(port) + ' -j REJECT -m comment --comment \'RRFSentinel - ' + type + ' - ' + indicatif + ' - ' + ban_clock + '\''
        try:
            os.system(cmd)
        except:
            pass
        f.write(datetime.datetime.now().strftime('%H:%M:%S %d-%m-%Y') + ban_comment + ' >> ' + cmd + '\n')

        # tcp
        cmd = 'sudo iptables -I INPUT -s ' + ip + ' -p tcp --dport ' + str(port) + ' -j REJECT -m comment --comment \'RRFSentinel - ' + type + ' - ' + indicatif + ' - ' + ban_clock + '\''
        try:
            os.system(cmd)
        except:
            pass
        f.write(datetime.datetime.now().strftime('%H:%M:%S %d-%m-%Y') + ban_comment + ' >> ' + cmd + '\n')
    return True

# Del iptable
def del_iptable(ip, port, indicatif, type, ban_clock):
    with open(s.path_log, 'a') as f:
        # udp
        cmd = 'sudo iptables -D INPUT -s ' + ip + ' -p udp --dport ' + str(port) + ' -j REJECT -m comment --comment \'RRFSentinel - ' + type + ' - ' + indicatif  + ' - ' + ban_clock + '\''
        try:
            os.system(cmd)
        except:
            pass        
        f.write(datetime.datetime.now().strftime('%H:%M:%S %d-%m-%Y') + ' << ' + cmd + '\n')
        # tcp
        cmd = 'sudo iptables -D INPUT -s ' + ip + ' -p tcp --dport ' + str(port) + ' -j REJECT -m comment --comment \'RRFSentinel - ' + type + ' - ' + indicatif  + ' - ' + ban_clock + '\''
        try:
            os.system(cmd)
        except:
            pass
        f.write(datetime.datetime.now().strftime('%H:%M:%S %d-%m-%Y') + ' << ' + cmd + '\n')
    return True