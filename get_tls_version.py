import ssl
import socket
import sys

TIMEOUT = 2

def get_tls_info(hostname: str, port: int = None) -> dict:
    try:
        port = port if port else 443
        sock = socket.create_connection((hostname, port), timeout=TIMEOUT)
        ssl_context = ssl.create_default_context()
        ssock = ssl_context.wrap_socket(sock, server_hostname=hostname)
        return {
            'version': ssock.version(),
            'cert_details': ssock.getpeercert(),
        }
    except Exception as e:
        raise e


if __name__ == '__main__':

    argv = sys.argv
    if len(argv) > 1:
        target = argv[1]
    else:
        exit(f"Must hostname and port to connect to. Example: {argv[0]} www.j5.org:443")

    target_hostname = target
    target_port = None
    if ":" in target:
        target_hostname, target_port = target.split(":")

    _ = get_tls_info(target_hostname, target_port)
    print(_)