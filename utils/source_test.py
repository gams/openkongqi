#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Command line tool to test whether extraction method works.

The user is to run the tests and compare the web data with the neatly
display data visually.

The table format will always appear as TIME, STATION, + accompanying
particular measurements (depends on the source).
"""

from __future__ import absolute_import, print_function, unicode_literals
from datetime import datetime
import argparse
import os

from openkongqi.utils import get_source

HTTP_TIMEOUT = 30

SOURCES = None


def fetch_and_extract(src_name):
    src = get_source(src_name)
    src_content = src.fetch()
    data = src.extract(src_content)
    return data


def get_categories(data):
    categories_set = set(
        reduce(lambda x, y: x + y,
               [r['fields'].keys()
                for uuid, records in data.items()
                for r in records])
    )
    return sorted(categories_set)


def display_table(data):
    # get info on categories for correct row format
    categories = get_categories(data)
    row_fmt = "{:^25} " + "{:^55} " + "{:>8} " * len(categories)
    col_names = ("TIME", "STATION", ) + tuple([c.upper() for c in categories])
    table = "\n" + row_fmt.format(*col_names)
    table += "\n" + row_fmt.format(*tuple(["-" * len(cn) for cn in col_names]))
    for uuid, records in data.items():
        for record in records:
            time = datetime.strftime(record['ts'], "%Y-%m-%d %H:%M:%S")
            row_data = (time, uuid, ) + tuple(record['fields'].get(c, '')
                                              for c in categories)
            table += "\n" + row_fmt.format(*row_data)
    print(table)


def create_parser():
    """Return command-line parser."""
    # setup parser
    parser = argparse.ArgumentParser()
    # list available sources
    parser.add_argument("-l", "--list-sources",
                        action="store_true",
                        help="list sources that are available")
    # okq custom configuration file
    parser.add_argument('--okqconf', dest='conffile', action='store',
                        type=str, help='path to a configuration file')
    # main input
    parser.add_argument("sources", nargs="*",
                        help="Name of a valid source. "
                        "See `okqconfig.py` for more help.",
                        type=str)

    return parser


def parse_args():
    """Parse command-line options."""
    parser = create_parser()
    args = parser.parse_args()

    if not args.sources and not args.list_sources:
        parser.error("Incorrect number of arguments.")

    if args.conffile is not None:
        os.environ.setdefault('OKQ_CONFMODULE', args.conffile)

    # run magic config after envvar is set
    from openkongqi.conf import settings
    global SOURCES
    SOURCES = settings['SOURCES']

    # print available choices, and exit program
    if args.list_sources:
        print()
        print("LIST OF AVAILABLE SOURCES")
        print("=========================")
        for src in sorted(SOURCES.keys()):
            print("    *  {}".format(src))
        print()
        exit()

    return args


def main():
    """Command-line entry."""
    args = parse_args()

    print()

    # ==== START :: Check if user selected all ====
    #
    # i.e.) "pm25.in:*" searches all keys beginning with "pm25.in:"
    #       if exists, then expand these selectors with their "children"
    #
    # ['aqhi.gov.hk:central', 'pm25.in:*] ==>
    # ['aqhi.gov.hk:central',
    #     'pm25.in:bejing', 'pm25.in:chengdu',
    #     'pm25.in:shanghai', 'pm25.in:yingkou']
    i = len(args.sources) - 1
    while i >= 0:
        if args.sources[i][-1] == "*":
            common_header = args.sources[i][:-1]
            children_sources = filter(
                lambda s: s[:len(common_header)] == common_header,
                SOURCES.keys()
            )
            args.sources = args.sources[:i] + \
                children_sources + args.sources[i + 1:]
            i += len(children_sources)
        i -= 1
    # ==== END :: Check if user selected all ====

    print("Selecting sources in order: {}".format(sorted(args.sources)))

    # fetch, extract, and display data
    for source in sorted(args.sources):
        data = fetch_and_extract(source)
        display_table(data)


if __name__ == '__main__':
    main()
