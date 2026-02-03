
USER_AGENT = "Python http.client"
TIMEOUT = 5

def make_request(fqdn: str, port: int = None, path: str = None, proxy_host: str = None, proxy_port: int = None):

    import http.client

    port = port if port else 443
    path = path if path else "/"
    path = f"/{path}" if not path.startswith("/") else path
    proxy_port = 3128 if proxy_port else 3128

    if port  == 443 or port == 8443:
        if proxy_host:
            conn = http.client.HTTPSConnection(proxy_host, port=proxy_port, timeout=TIMEOUT)
            conn.set_tunnel(host=fqdn, port=port)
        else:
            conn = http.client.HTTPSConnection(fqdn, port=port, timeout=TIMEOUT)
    else:
        if proxy_host:
            conn = http.client.HTTPConnection(proxy_host, port=proxy_port, timeout=TIMEOUT)
        else:
            conn = http.client.HTTPConnection(fqdn, port=port, timeout=TIMEOUT)

    # Make actual HTTP request
    headers = {'host': fqdn, 'User-agent': USER_AGENT}
    print("Sending request for:", fqdn, path)
    conn.request(method="GET", url=path, headers=headers)
    response = conn.getresponse()
    conn.close()
    return {
        'status': response.status,
        'reason': response.reason
    }


if __name__ == '__main__':

    from sys import argv
    from urllib.request import getproxies

    if len(argv) > 1:
        target = argv[1]
    else:
        exit(f"Must URL to connect to. Example: {argv[0]} https://www.j5.org:443")

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
