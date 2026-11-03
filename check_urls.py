#!/usr/bin/env python3

from socket import gethostbyname, create_connection, getaddrinfo, gethostname, gaierror, AI_CANONNAME
from time import time, mktime, strptime, localtime, timezone, altzone
from math import ceil
from ssl import create_default_context, SSLCertVerificationError, SSLError
from http.client import HTTPConnection, HTTPSConnection
from sys import argv, exit
from pathlib import Path
from getpass import getuser
from smtplib import SMTP
from itertools import chain
from urllib.parse import urlsplit
from urllib.request import getproxies
from prettytable import PrettyTable

DAYS_THRESHOLD = 11
TIMEOUT = 2
USER_AGENT = "Python http.client"
TLS_PORTS = (443, 8443)
TABLE_FIELDS = ("Target", "IP Address", "TLS Version", "SSL Cert", "Cert Expiration", "HTTP Status", "Notes")

def build_table(column_names, rows):

    t = PrettyTable()
    t.field_names = column_names
    for row in rows:
        t.add_row(row)
    return t


class Target:


    def __init__(self, target):

        url = target if target.startswith("https://") else f"https://{target}"
        url = f"{url}/" if "/" in target else url
        self.port = 443

        _ = urlsplit(url)
        self.hostname = _.hostname
        self.path = _.path
        if ":" in target:
            self.port = int(_.port)
        self.notes = ""
        self.is_resolvable = False
        self.is_reachable = False
        self.ip_address = None
        self.socket = None
        self.ssl_context = None
        self.secure_socket = None
        self.tls_version = None
        self.cert = {
            'common_name': None,
            'dns_names': [],
            'expiration_datetime': None,
        }
        self.cert_is_valid = False
        self.ca_cert = None
        self.http_status = None

    def check_dns(self):

        # Verify hostname resolves in DNS
        try:
            self.ip_address = gethostbyname(self.hostname)
            self.is_resolvable = True
        except gaierror as e:
            self.notes = "Not resolvable in DNS"
        except Exception as e:
            self.notes = str(e)
            #quit(e)

    def check_reachability(self):

        if not self.is_resolvable:
            return

        # Verify hostname is reachable on port
        try:
            self.socket = create_connection((self.ip_address, self.port), timeout=TIMEOUT)
            self.is_reachable = True
        except ConnectionRefusedError:
            self.is_reachable = False
            self.notes = f"Not reachable on port {self.port}"
        except TimeoutError:
            self.is_reachable = False
            self.notes = f"Connection timed out on port {self.port}"

    def check_tls(self):

        if not self.is_reachable:
            return

        # Perform SSL/TLS handshake
        try:
            self.ssl_context = create_default_context()
            self.secure_socket = self.ssl_context.wrap_socket(sock=self.socket, server_hostname=self.hostname)
            if secure_socket_version := self.secure_socket.version():
                if 'TLSv' in secure_socket_version:
                    self.tls_version = float(secure_socket_version.replace('TLSv', ""))
                    if self.tls_version < 1.2:
                       self.notes = "Does not support TLS 1.2 or higher"
            if cert_details := self.secure_socket.getpeercert():
                #print(cert_details)
                common_name = self.hostname
                dns_names = []
                if cert_subject := cert_details.get('subject'):
                    common_name = [_[1] for _ in list(chain(*cert_subject)) if 'commonName' in _][0]
                if subject_alt_name := cert_details.get('subjectAltName'):
                    for _ in subject_alt_name:
                        if 'DNS' in _:
                            dns_names.append(_[1])

                if not_before := cert_details.get('notBefore'):
                    issued_timestamp = round(mktime(strptime(not_before, "%b %d %H:%M:%S %Y %Z")))
                else:
                    issued_timestamp = 0
                if not_after := cert_details.get('notAfter'):
                    expiration_timestamp = round(mktime(strptime(not_after, "%b %d %H:%M:%S %Y %Z")))
                else:
                    expiration_timestamp = 0
                self.cert.update({
                    'common_name': common_name,
                    'dns_names': dns_names,
                    'issued_datetime': not_before,
                    'issued_timestamp': issued_timestamp,
                    'expiration_timestamp': expiration_timestamp,
                    'expiration_datetime': not_after,
                })
                self.cert_is_valid = True
                return True
        except SSLCertVerificationError as e:
            self.tls_version = None
            self.notes = "Invalid SSL cert"
        except SSLError as e:
            self.tls_version = 0.0
            self.notes = "SSL Handshake failure"
        except Exception as e:
            self.notes = format(e)
            quit(self.notes)

    def check_http(self) -> bool:

        if not self.is_reachable:
            return False

        try:
            if self.port in TLS_PORTS:
                conn = HTTPSConnection(self.hostname, self.port, timeout=TIMEOUT, context=self.ssl_context)
            else:
                conn = HTTPConnection(self.hostname, self.port, timeout=TIMEOUT)
            conn.request(method="GET", url=self.path, headers={'User-agent': USER_AGENT})
            resp = conn.getresponse()
            self.http_status = f"{str(resp.status)} {str(resp.reason)}" if resp.reason else str(resp.status)
            if 500 <= int(self.http_status[:3]) < 600:
                self.notes = "HTTP 5xx response"
            else:
                return True
        except:
            self.http_status = None
        return False

    def calc_cert_expiration(self):

        if not self.cert:
            return

        # Adjust for local timezone setting
        local_timezone_offset = timezone if (localtime().tm_isdst == 0) else altzone
        current_timestamp = round(time()) + local_timezone_offset

        # Do math to determine days, hour, seconds remaining until expiration
        seconds_until_expiration = self.cert['expiration_timestamp'] - current_timestamp
        hours_until_expiration = ceil(seconds_until_expiration / 3600)
        days_until_expiration = hours_until_expiration // 24
        self.cert.update({
            'seconds_until_expiration': seconds_until_expiration,
            'hours_until_expiration': hours_until_expiration,
            'days_until_expiration': days_until_expiration,
        })
        if days_until_expiration <= DAYS_THRESHOLD:
            if seconds_until_expiration <= 0:
                self.notes = f"Certificate expired on {self.cert['expiration_datetime']}"
            if days_until_expiration <= 2:
                self.notes = f"Cert expires in {hours_until_expiration} hours!!!"
            else:
                self.notes = f"Cert expires in {days_until_expiration} days"

def read_urls_list(input_file):

    urls = []
    p = Path(input_file)
    if p.exists() and p.is_file():
        lines = p.read_text().splitlines()
        urls = [line.strip() for line in lines if line and not line.startswith("#")]
    else:
        exit("Can't open file: '" + input_file + "'")

    return urls


def main():

    proxies = getproxies()
    if len(argv) < 2:
        exit("Usage: " + argv[0] + " 'urls_file'")
    input_file = argv[1]
    recipient = None
    if len(argv) > 2:
        recipient = argv[2]
    if len(argv) > 3:
        sender = argv[3]
    else:
        sender = getuser() + "@" + getaddrinfo(gethostname(), 0, flags=AI_CANONNAME)[0][3]

    hostnames = read_urls_list(input_file)

    results = []
    for hostname in hostnames:

        target = Target(hostname)
        target.check_dns()
        target.check_reachability()
        if target.port in TLS_PORTS:
            target.check_tls()
            if target.cert_is_valid:
                target.calc_cert_expiration()
        target.check_http()

        results.append([
            target.hostname + ":" + str(target.port),
            target.ip_address,
            target.tls_version,
            target.cert['common_name'],
            target.cert['expiration_datetime'],
            target.http_status,
            target.notes
            ]
        )

    output = build_table(TABLE_FIELDS, results)

    notes = [result[4] for result in results ]
    if recipient and len(notes) > 0:
        subject = "Site Issue"
        message = f"From: {sender}\nTo: {recipient}\nSubject: {subject}\n{output}"
        try:
            server = SMTP('localhost', port=25)
            server.ehlo()
            server.sendmail(sender, recipient, message)
            server.quit()
        except Exception as e:
            print(e)
    else:
        print(output)

if __name__ == "__main__":

    start_time = time()
    main()
    print("seconds_to_execute:", round((time() - start_time), 3))

