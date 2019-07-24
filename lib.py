#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
RRFSentinel
Learn more about RRF on https://f5nlg.wordpress.com
73 & 88 de F4HWN Armel
'''

# Usage
def usage():
    print 'Usage: RRFSentinel.py [options ...]'
    print
    print '--help                           cet aide'
    print
    print 'Parametrages:'
    print 
    print '  --declenchement    nombre      nombre de déclenchement inférieur à 3 secondes'
    print '  --plage            nombre      durée de la plage de déclenchements, en minutes'
    print '  --ban              nombre      durée de la quarantaine, en minutes'
    print
    print '88 & 73 from F4HWN Armel'

# Cette fonction renvoie le nom du link afin de trier la liste.
def fctSort(e):
    n = e.split(':')
    return n[3].strip()

# readbip lit le fichier BIP.txt pour alimentre le dictionnary bip
def readbip():
    f = open('/root/BIP.txt','r')
    for x in f:
      e = x.split(":")
      bip[e[0]] = e[1]
    f.close()

# writebip sauvegarde le dictionnary bip dans BIP.txt.
def writebip():
    f = open('/root/BIP.txt','w')
    for n in bip:
      txt = n + ':' + bip[n] + ':\n'
      f.write(txt)
    f.close()

def writelog(txt):
    fl=open('/root/blockIP.log','a')
    fl.write(txt)
    fl.close()

# lecture du svxreflector.log
def readlog():    
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
        