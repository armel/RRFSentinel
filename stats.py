#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
RRFSentinel
Learn more about RRF on https://f5nlg.wordpress.com
73 & 88 de F4HWN Armel
'''

import os
import sys

# Save stats
def save_stat(stat, indicatif, ban_time):
    try:
        stat[indicatif][0] += 1
        stat[indicatif][1] += ban_time
    except KeyError:
        stat[indicatif] = [1, ban_time]

    return stat

def main():

    stat = dict()

    with open('/tmp/RRFSentinel.log') as f:
        for line in f:
            if ' - ' in line:
                element = line.split(' - ')
                if '<<' not in element[1]:
                    stat = save_stat(stat, element[1], int(element[4]))

    stat = sorted(stat.items(), key=lambda x: x[1][1])
    stat.reverse()

    for s in stat:
        print s[0] + ':\t',
        print '%03d' % s[1][1],
        print ' minutes, pour ',
        print '%03d' % s[1][0],
        if s[1][0] > 1:
            print ' bans'
        else:
            print ' ban'


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass