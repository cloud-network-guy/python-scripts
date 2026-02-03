import http.client

PROXY = {'host': "100.77.77.101", 'port': 3128}
TARGET = {'host': "www.hightail.com", 'port': 80, 'url': "/u/john-heyer"}
HEADERS = {'host': TARGET.get('host'), 'User-agent': "Python http.client"}
TIMEOUT = 10

if port := TARGET.get('port') == 443:
    conn = http.client.HTTPSConnection(PROXY.get('host'), port=PROXY.get('port'), timeout=TIMEOUT)
    conn.set_tunnel(host=TARGET.get('host'), port=TARGET.get('port', 443))
else:
    conn = http.client.HTTPConnection(PROXY.get('host'), port=PROXY.get('port'), timeout=TIMEOUT)
conn.request(method="GET", url=TARGET.get('url', "/"), headers=HEADERS)
response = conn.getresponse()
conn.close()
print(response.status, response.reason)
