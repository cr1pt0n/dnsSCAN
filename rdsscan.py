# -*- coding: utf-8 -*-

import os
import socket
import sys
import argparse
import time
import requests

os.system('cls' if( os.name == 'nt' ) else 'clear')

try:
    import dns.resolver
    import dns.query
    import dns.zone

except ImportError:
    print RED + 'Modulos (python dns-python) não instalados!'
    sys.exit()

# Cores 

RED = '\033[1;31m'
BLUE = '\033[94m'
GREEN = '\033[1m'
YELLOW = '\033[33m'
ENDC = '\033[0m'

logo = RED + '''
____________  _____                   
| ___ \  _  \/  ___|   coded by: RNX                
| |_/ / | | |\ `--.       _ __  _   _ 
|    /| | | | `--. \     | '_ \| | | |
| |\ \| |/ / /\__/ /  _  | |_) | |_| |
\_| \_|___/  \____/  (_) | .__/ \__, |
                         | |     __/ |
                         |_|    |___/ 
'''

help = GREEN + '* Usage: {} -d <dominio.com> -w <wordlist> -s <salvar subdomains>\n'.format(sys.argv[0])

parser = argparse.ArgumentParser()
parser.add_argument('-d', '--dominio', help='Dominio alvo', action='store')
parser.add_argument('-w', '--wordlist', help='Sua wordlist', action='store')
parser.add_argument('-s', '--save', help='Salvar subdomains em um arquivo.txt', action='store_true')
argumentos = parser.parse_args()

target = argumentos.dominio
wordlist = argumentos.wordlist

if( len(sys.argv) == 1 ):
    print logo
    print help
    sys.exit()

if( target is None ):
    print help
    sys.exit()

def mail_servers():
    global target
    global dns

    print BLUE + '---- {} ----\n'.format(target)
    dns = dns.resolver.Resolver()
    mxs = dns.query(target, 'MX')

    print RED + '\nMail (MX) Servers: '
    print RED + '_________________\n'
    
    for mx in mxs:
        if( len(str(mx.exchange)) > 23 ):
            print ENDC + str(mx.exchange) + '\t' + 'IN\t' + 'A\t' + socket.gethostbyname(str(mx.exchange))
        elif( len(str(mx.exchange)) > 15 and len(str(mx.exchange)) <= 23 ):
            print ENDC + str(mx.exchange) + '\t\t' + 'IN\t' + 'A\t' + socket.gethostbyname(str(mx.exchange))
        else:
            print ENDC + str(mx.exchange) + '\t\t\t' + 'IN\t' + 'A\t' + socket.gethostbyname(str(mx.exchange))
  
def name_servers():
    import dns.resolver
    global target

    nss = dns.resolver.query(str(target), 'NS')

    print RED + '\nName (NS) Servers: '
    print RED + '_________________\n'

    for ns in nss:
        print ENDC + str(ns) + '\t' + '\tIN\t' + 'A\t' + socket.gethostbyname(str(ns))

def transfer_zona():
    global target
    import dns.zone

    try:
        ip = socket.gethostbyname(target)

        print RED + '\nTrying zone transfer: '
        print RED + '_____________________\n ' + ENDC
          
        zone = dns.zone.from_xfr(dns.query.xfr(ip, str(target), relativize=False), relativize=False)
        nomes = zone.nodes.keys()
        nomes.sort()

        print nomes[1]
        for n in nomes:
            print zone[n].to_text(n)

    except socket.error:
        print RED + 'Transfer zone failed !!!\n'

def verifica_bf():
    if( '-w' not in sys.argv and '--wordlist' not in sys.argv ):
        print BLUE + '\nBrute Force not specified bye...'
        sys.exit()

    else:
        brute_sub(wordlist)    

def brute_sub(wordlist):
    import dns.resolver
    global target

    dominioss = []
    founds = ''

    print RED + '\nBrute Forcing in subdomains:'
    print RED + '______________________________\n'
    
    try:
        with open(wordlist) as subdomains:
            subs = subdomains.readlines()

            for s in subs:
                dominioss.append(s.strip('\n'))
    except IOError:
        print RED + '\nWordlist not found !'
        sys.exit()

    d = dns.resolver.Resolver()
    
    try:
        for subs in dominioss:
            try:
                    a = d.query(subs + '.' + target, 'A')
                    for i in a:
                        print ENDC + str(i) + ' - ' + str(subs) + '.' + str(target)
                        founds += (str(subs) + '.' + str(target) + '\n')
            except dns.resolver.NXDOMAIN:
                continue
    except dns.resolver.NoAnswer:
        pass

    if( '-s' in sys.argv or '--save' in sys.argv ):
        with open('subdomains.txt', 'w') as salvar:
            salvar.write(founds + '\n')
            print RED + '\n[*] Saving subdomains found in "subdomains.txt"'
            salvar.close()

def main():
    global target
    global wordlist
    global save

    mail_servers()
    name_servers()
    transfer_zona()
    verifica_bf()

if( __name__ == '__main__' ):
    main()