import re
from urllib.parse import urlparse

import idna


RE_IP_ADDR = re.compile(r"^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$")
RE_HOST_WITH_PORT = re.compile(r':\d+')


class InvalidUrl(Exception):
    pass


def parse_domain(url: str) -> str:
    full_hostname = urlparse(url).netloc
    full_hostname = RE_HOST_WITH_PORT.sub('', full_hostname)  # for cutting ports - "https://example.com:8080"

    if RE_IP_ADDR.match(full_hostname):  # checking is the hostname ip address
        return full_hostname

    if full_hostname.startswith('xn--'):  # 3. idna decode (xn----7sbgbbkedzyymg.xn--p1ai)
        full_hostname = idna.decode(full_hostname)

    parts = full_hostname.split('.')
    try:
        domain = f'{parts[-2]}.{parts[-1]}'
    except IndexError:
        raise InvalidUrl(url)
    return domain
