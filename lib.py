#!/usr/bin/env python2
# -*- coding: utf-8 -*-

'''
RRFSentinel
Learn more about RRF on https://f5nlg.wordpress.com
73 & 88 de F4HWN Armel
'''

import settings as s

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
    
    return sum([a * b for a, b in zip(format, map(int, time.split(':')))])