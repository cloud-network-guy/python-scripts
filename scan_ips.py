#!/usr/bin/env python3

import sys
import socket
import ipaddress

PORT = 22
TIMEOUT = 2


def scan_ip(ip: str) -> bool:

    ip = ip.split('/')[0] if '/' in ip else ip
    try:
        sock = socket.create_connection((ip, int(PORT)), timeout=TIMEOUT)
        return True
    except:
        return False



if __name__ == "__main__":

    argv = sys.argv
    if len(argv) > 1:
        network = argv[1]
    else:
        exit(f"Must provide subnet as parameter.  Example: {argv[0]} 192.168.1.0/24")

    _, mask = network.split('/')
    network_addr = ipaddress.ip_network(network)
    power = 32 - int(mask)
    hosts = list(network_addr.subnets(power))
    #print(hosts)
    for host in hosts:
        host = str(host)
        print("Scanning host:", host)
        if scan_ip(host):
            print(host)
