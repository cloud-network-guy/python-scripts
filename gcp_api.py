#!/usr/bin/env python3

import platform
import google.auth
import requests


url = "https://compute.googleapis.com/compute/v1/projects/otc-core-network-prod-4aea/global/urlMaps/ncs1-https"

SCOPES = ['https://www.googleapis.com/auth/cloud-platform']
VERIFY_SSL = False
REQUESTS_VERSION = requests.__version__
PYTHON_VERSION = platform.python_version()
PLATFORM_SYSTEM = platform.system()
PLATFORM_MACHINE = platform.machine()
USER_AGENT = f"Requests/{REQUESTS_VERSION} ({PLATFORM_SYSTEM}; {PLATFORM_MACHINE}) Python/{PYTHON_VERSION}"


def make_request(url, headers):

    import json

    r = requests.get(url, headers = headers)
    return r.json()

def main():

    from google.auth.transport.requests import Request

    credentials, project_id = google.auth.default(scopes=SCOPES, quota_project_id=None)
    credentials.refresh(Request())
    access_token = credentials.token
    headers = {
        'User-Agent': USER_AGENT,
        'Authorization': f"Bearer {access_token}",
    }
    _ = make_request(url, headers)
    return _

if __name__ == "__main__":

    from pprint import pprint
    from traceback import format_exc

    try:
        _ = main()
        pprint(_)
    except Exception as e:
        quit(format_exc())



