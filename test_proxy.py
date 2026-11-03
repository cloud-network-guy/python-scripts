#!/usr/bin/env python3

USER_AGENT = "Python http.client"
TIMEOUT = 5
PLAIN_HTTP_PORTS = (80, 8080)
DEFAULT_HTTPS_PORT = 443
DEFAULT_PROXY_PORT = 3128
DEFAULT_PATH = "/"
EXAMPLE_TARGET = "www.j5.org:443"

def make_request(fqdn: str, port: int = None, path: str = None, proxy_host: str = None, proxy_port: int = None):

    from http.client import HTTPSConnection, HTTPConnection

    port = port if port else DEFAULT_HTTPS_PORT
    path = path if path else DEFAULT_PATH
    path = f"/{path}" if not path.startswith("/") else path
    proxy_port = proxy_port if proxy_port else DEFAULT_PROXY_PORT

    if port in PLAIN_HTTP_PORTS:
        if proxy_host:
            conn = HTTPConnection(proxy_host, port=proxy_port, timeout=TIMEOUT)
        else:
            conn = HTTPConnection(fqdn, port=port, timeout=TIMEOUT)
    else:
        # It's 2026, let's default to TLS
        if proxy_host:
            conn = HTTPSConnection(proxy_host, port=proxy_port, timeout=TIMEOUT)
            conn.set_tunnel(host=fqdn, port=port) # RFC 7230
        else:
            conn = HTTPSConnection(fqdn, port=port, timeout=TIMEOUT)

    # Make actual HTTP request
    headers = {'host': fqdn, 'User-agent': USER_AGENT}
    print("Sending request for:", fqdn, path)
    conn.request(method="GET", url=path, headers=headers)
    response = conn.getresponse()
    conn.close()

    return {
        'status': response.status,
        'reason': response.reason,
        'server': response.headers.get('server', "unknown"),
        'via': response.headers.get('via', "None"),
    }


if __name__ == '__main__':

    from sys import argv
    from urllib.request import getproxies

    if len(argv) > 1:
        target = argv[1]
    else:
        exit(f"Must URL to connect to. Example: {argv[0]} {EXAMPLE_TARGET}")

    proxies = getproxies()
    if len(argv) > 2:
        proxy = argv[2]
    else:
        if not proxies:
            quit(f"Proxy must be set via environment variable or specified via CLI.")
        print("Proxies:", proxies)

    target_fqdn = None
    target_port = None
    target_path = None
    if ":" in target:
        target_fqdn, target_port = target.split(":")
    if "/" in target:
        target_fqdn, target_path = target.split("/")
    _ = make_request(target_fqdn, target_port, target_path)
    print(_)
