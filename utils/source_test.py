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
from collections import OrderedDict
from datetime import datetime
from importlib import import_module
import argparse
import logging

from openkongqi.conf import settings
from openkongqi.exceptions import SourceError

HTTP_TIMEOUT = 30
LOGGING_FORMAT = "%(asctime)s [ %(levelname)-8s ] %(message)s"
LOGGING_LEVEL = logging.DEBUG

logger = logging.getLogger(__name__)
logging.basicConfig(format=LOGGING_FORMAT, level=LOGGING_LEVEL)


def fetch_and_extract(src_name):
    if src_name not in settings['SOURCES']:
        raise SourceError("Unknown source ({})".format(src_name))
    modname = settings['SOURCES'][src_name]['modname']
    mod = import_module("." + modname, 'openkongqi.source')
    src = mod.Source(src_name)
    src_content = src.fetch()
    data_points = src.extract(src_content)
    return data_points


def get_categories(data_points):
    distinct_times = set([dp[0] for dp in data_points])
    distinct_stations = set([dp[1] for dp in data_points])
    num_categories = \
        len(data_points) / len(distinct_times) / len(distinct_stations)
    return [dp[2] for dp in data_points[:num_categories]]


def display_table(data_points):
    # group by time and station
    grouped_dp = OrderedDict()
    for time, station, category, value in data_points:
        time = datetime.strftime(time, "%Y-%m-%d %H:%M:%S")
        if time not in grouped_dp:
            grouped_dp[time] = OrderedDict()
        if station not in grouped_dp[time]:
            grouped_dp[time][station] = OrderedDict()
        grouped_dp[time][station][category] = str(value)

    # get info on categories for correct row format
    categories = get_categories(data_points)
    row_fmt = "{:^25} " + "{:^35} " + "{:>8} " * len(categories)
    col_names = ("TIME", "STATION", ) + tuple([c.upper() for c in categories])
    table = "\n" + row_fmt.format(*col_names)
    table += "\n" + row_fmt.format(*tuple(["-" * len(cn) for cn in col_names]))
    for time, info in grouped_dp.items():
        for station, measurements in info.items():
            row_data = ((time, station, ) + tuple(measurements.values()))
            table += "\n" + row_fmt.format(*row_data)
    print(table)


def create_parser():
    """Return command-line parser."""
    # setup parser
    parser = argparse.ArgumentParser()
    # group for logging levels
    log_level = parser.add_mutually_exclusive_group()
    log_level.add_argument("--debug", action="store_true")
    log_level.add_argument("--info", action="store_true")
    log_level.add_argument("--warning", action="store_true")
    log_level.add_argument("--error", action="store_true")
    log_level.add_argument("--critical", action="store_true")
    # list available sources
    parser.add_argument("-l", "--list-sources",
                        action="store_true",
                        help="list sources that are available")
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

    # print available choices, and exit program
    if args.list_sources:
        print()
        print("LIST OF AVAILABLE SOURCES")
        print("=========================")
        for src in sorted(settings['SOURCES'].keys()):
            print("    *  {}".format(src))
        print()
        exit()

    # set logging level based on options
    if args.debug:
        logger.setLevel(logging.DEBUG)
    elif args.warning:
        logger.setLevel(logging.WARNING)
    elif args.error:
        logger.setLevel(logging.ERROR)
    elif args.critical:
        logger.setLevel(logging.CRITICAL)
    else:  # logging level set to INFO by default
        logger.setLevel(logging.INFO)

    return args


def main():
    """Command-line entry."""
    args = parse_args()

    print()

    # check if user selected all
    # i.e.) "pm25.in/*" searches all keys beginning with "pm25.in/"
    #       if exists, then replace these selectors with their "children"
    # ['aqhi.gov.hk/central', 'pm25.in/*] ==>
    # ['aqhi.gov.hk/central',
    #     'pm25.in/bejing', 'pm25.in/chengdu', 'pm25.in/shanghai', 'pm25.in/yingkou']
    i = len(args.sources) - 1
    while i >= 0:
        if args.sources[i][-1] == "*":
            common_header = args.sources[i][:-1]
            children_sources = filter(
                lambda s: s[:len(common_header)] == common_header,
                settings['SOURCES'].keys()
            )
            args.sources = args.sources[:i] + \
                children_sources + args.sources[i + 1:]
            i += len(children_sources)
        i -= 1

    logger.debug("Selecting sources in order: {}".
                 format(sorted(args.sources)))

    # fetch, extract, and display data
    for source in sorted(args.sources):
        data_points = fetch_and_extract(source)
        display_table(data_points)


if __name__ == '__main__':
    main()
