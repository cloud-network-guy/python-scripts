#!/usr/bin/env python3

import sys
import socket
import ipaddress

PORT = 22
TIMEOUT = 2


def scan_ip(ip: str, port: int) -> bool:

    ip = ip.split('/')[0] if '/' in ip else ip
    try:
        sock = socket.create_connection((ip, int(port)), timeout=TIMEOUT)
        return True
    except:
        return False

def main():

    argv = sys.argv
    if len(argv) > 1:
        network = argv[1]
        port = int(argv[2]) if len(argv) > 2 else PORT
    else:
        sys.exit(f"Must provide subnet as parameter.  Example: {argv[0]} 192.168.1.0/24")

    _, mask = network.split('/')
    network_addr = ipaddress.ip_network(network)
    power = 32 - int(mask)
    hosts = list(network_addr.subnets(power))
    #print(hosts)
    for host in hosts:
        host = str(host)
        print("Scanning host ", host, "on port", port)
        if scan_ip(host, port):
            print(host)


if __name__ == '__main__':

    main()
