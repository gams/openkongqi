# -*- coding: utf-8 -*-
import argparse
import distutils.spawn
import os
import sys

from celery.bin.celery import main as clry_main
from celery.utils.imports import find_module, import_from_cwd, NotAPackage

# fix path issues when running `okq-server`
sys.path.insert(0, os.getcwd())


def load_confmod(parser, confmod):
    # import here so we can fix the sys.path when running the script directly
    from openkongqi.conf import config_from_object

    if confmod is None:
        parser.print_help()
        sys.exit(1)

    try:
        find_module(confmod)
    except (ImportError, NotAPackage):
        sys.stderr.write("configuration parameter is not a module"
                "({})\n".format(confmod))
        parser.print_help()
        sys.exit(1)

    mod = import_from_cwd(confmod)
    config_from_object(mod)


def okq_init():
    parser = argparse.ArgumentParser(
        description="initialize database for records",
        epilog="Any extra argument is directly passed to celery, celery's"
        " `--config' argument will be replaced by the value of '--okqconf'")
    parser.add_argument('--okqconf', dest='confmod', action='store',
                        type=str, help='path to a configuration file')
    args = parser.parse_args()

    load_confmod(parser, args.confmod)

    # run magic configuration after environment variable is set
    import openkongqi.conf
    openkongqi.conf.recsdb.db_init()


def okq_server():
    # import here so we can fix the sys.path when running the script directly
    from openkongqi.exceptions import OpenKongqiError

    parser = argparse.ArgumentParser(
        description='outdoor air quality data',
        epilog="Any extra argument is directly passed to celery, celery's"
        " `--config' argument will be replaced by the value of '--okqconf'")
    parser.add_argument('--okqconf', dest='confmod', action='store',
            type=str, help='path to a configuration module (mandatory)')
    args, clry_args = parser.parse_known_args()

    load_confmod(parser, args.confmod)

    # reproduce sys.argv to call celery
    clry_args.insert(0, distutils.spawn.find_executable('celery'))
    try:
        clry_main(clry_args)
    except OpenKongqiError as e:
        sys.stderr.write(e.message + "\n")
        sys.exit(1)


if __name__ == '__main__':          # pragma: no cover
    okq_server()
