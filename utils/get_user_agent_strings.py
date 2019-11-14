# -*- coding: utf-8 -*-

import argparse
import json
import logging
import socket
from time import time
from urllib.error import URLError, HTTPError
from urllib.request import urlopen

from bs4 import BeautifulSoup

UA_LINKS = {
    "Chrome": "http://www.useragentstring.com/pages/Chrome/",
    "Internet Explorer": "http://www.useragentstring.com/pages/Internet%20Explorer/",
    "Midori": "http://www.useragentstring.com/pages/Midori/",
    "Opera": "http://www.useragentstring.com/pages/Opera/",
    "Safari": "http://www.useragentstring.com/pages/Safari/"
}

HTTP_TIMEOUT = 30
LOGGING_FORMAT = "%(asctime)s [%(levelname)s] %(message)s"
LOGGING_LEVEL = logging.DEBUG

logger = logging.getLogger(__name__)
logging.basicConfig(format=LOGGING_FORMAT, level=LOGGING_LEVEL)


def fetch_ua_url_content(url, user_agent_category):
    """Fetch url, catching exceptions along the way
    """
    try:
        logger.info("Attempting to fetch user agent data for %s...",
                    user_agent_category)
        resp = urlopen(url, timeout=HTTP_TIMEOUT)
    except HTTPError as err:
        logger.error("Data fetch failed due to HTTP error: %s %s",
                     err.code, err.reason)
        return None
    except URLError as err:
        if isinstance(err.reason, socket.timeout):
            logger.critical("Data fetch interrupted: HTTP timeout")
            return None
        else:
            logger.error("Data fetch failed due to URL err no. %s",
                         str(err.reason)[7:].replace(']', ':'))
            return None

    logger.info("Data successfully fetched!")
    logger.debug("Fetch status: HTTP %s" % (resp.getcode()))
    return resp


def extract_user_agents(ua_list_resp):
    """Extract contents of the user agent list page using BeautfulSoup

    Naive implementation - returns a list.
    """
    logger.debug("Converting raw data into BeautifulSoup data structure ...")
    bs_start_time = time()
    soup = BeautifulSoup(ua_list_resp)
    bs_stop_time = time()
    logger.debug("Converted in %.4f seconds" % (bs_stop_time - bs_start_time))
    liste = soup.find('div', {'id': 'liste'})
    ua_strings = map(lambda x: x.text, liste.find_all('li'))
    return ua_strings


def main():
    # set up parser
    parser = argparse.ArgumentParser()
    parser.add_argument("file",
                        help="Name of output file",
                        type=argparse.FileType('wt'))
    args = parser.parse_args()
    logger.debug("Set output file as {}"
                 .format(args.file.name))
    # scrape html and extract content
    ua_list = []
    for category, url in UA_LINKS.items():
        user_agents = extract_user_agents(
            fetch_ua_url_content(url, category))
        ua_list.extend(user_agents[:3])  # just the first three
    # dump content into file as specified from command line
    with open(args.file.name, 'w') as f:
        json.dump(ua_list, f, indent=4, separators=(',', ': '))


if __name__ == '__main__':
    main()
