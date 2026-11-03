import sys
import platform
import aiohttp
import traceback
import urllib.request
import os
import asyncio

EXPECTED_RESPONSE = 200
NUM_REQUESTS = 32
VERIFY_SSL = False
PYTHON_VERSION = sys.version.split(' ')[0]
PLATFORM_SYSTEM = platform.system()
PLATFORM_MACHINE = platform.machine()
AIOHTTP_VERSION = aiohttp.__version__
USER_AGENT = f"AIOHTTP/{AIOHTTP_VERSION} ({PLATFORM_SYSTEM}; {PLATFORM_MACHINE}) Python/{PYTHON_VERSION}"


async def make_request(session: aiohttp.ClientSession, url: str, proxy: str = None) -> bool:

    headers = {'User-Agent': USER_AGENT}
    params = {}

    try:
        async with (session.get(url, headers=headers, params=params, proxy=proxy, ssl=VERIFY_SSL) as response):
            if int(response.status) == EXPECTED_RESPONSE:
                return True
            else:
                return False
    except Exception as e:
        raise RuntimeWarning(e)


async def make_requests(url: str, num_requests: int = 10) -> list:

    protocol = "http" if URL.startswith("http://") else "https"
    if proxies := urllib.request.getproxies():
        proxy = proxies.get(protocol)
    else:
        for e in ["PROXY", "proxy"]:
            if proxy := os.environ.get(e):
                break
    if proxy:
        print(f"{protocol} Proxy Detected:", proxy)
    session = aiohttp.ClientSession(raise_for_status=False)
    tasks = [make_request(session, url, proxy) for i in range(0, num_requests)]
    _ = await asyncio.gather(*tasks)
    await session.close()
    return _

def main():

    argv = sys.argv
    if len(argv) > 1:
        url = argv[1]
        num_requests = int(argv[2]) if len(argv) > 2 else NUM_REQUESTS
    else:
        exit(f"Must supply URL to connect to")

    _ = asyncio.run(make_requests(url, num_requests))
    if all(_):
        print(f"All {num_requests} requests were successful.")
    else:
        print(f"Some requests were not successful.")
        sys.exit(traceback.format_exc())


if __name__ == '__main__':

    main()
