#!/usr/bin/env python3

from quart import Quart, request, Response, jsonify
from traceback import format_exc

PLAIN_TEXT_CONTENT_TYPE = "text/plain"
ERROR_CODE = 500

app = Quart(__name__)

@app.route("/ping")
def _ping():

    from platform import node, platform

    try:
        _ = f"Hello from {node()} running {platform()}\n"
        return Response(_, 200, content_type=PLAIN_TEXT_CONTENT_TYPE)
    except Exception as e:
        return Response(format_exc(), ERROR_CODE, content_type=PLAIN_TEXT_CONTENT_TYPE)


@app.route("/geoip")
@app.route("/geoip/")
@app.route("/geoip/<path:path>")
def _geoip(path=None):

    from geoip import GeoIPList

    if path:
        ip_list = path.split('/') if '/' in path else [path]
    else:
        if x_real_ip := request.headers.get('X-Real-IP'):
            ip_list = [x_real_ip]
        else:
            ip_list = [request.remote_addr]
    try:
        _ = GeoIPList(ip_list)
        return jsonify(_.geoips)
    except Exception as e:
        return Response(format(e), ERROR_CODE, content_type=PLAIN_TEXT_CONTENT_TYPE)


if __name__ == '__main__':
    app.run(debug=True)
