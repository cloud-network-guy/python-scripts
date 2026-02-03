import aiohttp
import sys
import platform

URL = "https://learningcompass.learnflex.net/users/index.asp"
EXPECTED_RESPONSE = 401
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


async def main() -> list:

    from urllib.request import getproxies
    from os import environ
    from asyncio import gather

    protocol = "http" if URL.startswith("http://") else "https"
    if proxies := getproxies():
        proxy = proxies.get(protocol)
    else:
        for e in ["PROXY", "proxy"]:
            if proxy := environ.get(e):
                break
    if proxy:
        print(f"{protocol} Proxy Detected:", proxy)
    session = aiohttp.ClientSession(raise_for_status=False)
    tasks = [make_request(session, URL, proxy) for i in range(0, NUM_REQUESTS)]
    _ = await gather(*tasks)
    return _

if __name__ == '__main__':

    from asyncio import run

    _ = run(main())
    if all(_):
        print(f"All {NUM_REQUESTS} requests were successful.")
    else:
        print(f"Some requests were not successful.")
