# -*- coding: utf-8 -*-
"""
Naive settings for openkongqi

Very naive approach for settings management. Create an env variable
'OKQ_CONFMODULE' with the name of a configuration module to setup openkongqi.

No lazy loading, all straight talk!
"""

from __future__ import absolute_import, print_function, unicode_literals
from importlib import import_module
import logging.config
import os
import sys

from .exceptions import ConfigError, SourceError
from .utils import load_tree, dig_loader
from .status.base import create_statusdb
from .records.base import create_recsdb


here = os.path.abspath(os.path.dirname(__file__))

DEFAULT_LOGGING = {
    'disable_existing_loggers': False,
    'formatters': {
        'brief': {
            'format': '%(asctime)s | %(name)s | %(levelname)s | %(message)s'
        },
        'precise': {
            'format': '%(asctime)s [ %(levelname)s ] <PID %(process)d:%(processName)s> %(name)s.%(funcName)s(): %(message)s'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'brief',
            'level': 'DEBUG',
            'stream': 'ext://sys.stdout'
        },
        'info_file_handler': {
            'backupCount': 20,
            'class': 'logging.handlers.RotatingFileHandler',
            'encoding': 'utf8',
            'filename': '',  # loaded with global_settings['LOGFILE']
            'formatter': 'precise',
            'level': 'INFO',
            'maxBytes': 10485760
        },
    },
    'incremental': False,
    'loggers': {
        '': {
            'handlers': ['info_file_handler'],
            'level': 'DEBUG',
            'propagate': False
        },
    },
    'root': {
        'handlers': ['info_file_handler'],
        'level': 'DEBUG'
    },
    'version': 1,
}

CONFMODULE = 'okqconfig'
os.environ.setdefault('OKQ_CONFMODULE', CONFMODULE)

# default settings
global_settings = {
    'CACHE': '_cache',
    'DATABASES': {
        'status': {
            'ENGINE': 'openkongqi.status.redis_db',
            'NAME': '',
            'USER': '',
            'PASSWORD': '',
            'HOST': 'localhost',
            'PORT': '6379',
            'DB_ID': 1,
        },
        'records': {
            'ENGINE': 'openkongqi.records.sqlite3',
            'NAME': 'openkongqi',
        }
    },
    'LOGGING': DEFAULT_LOGGING,
    'LOGFILE': 'openkongqi.log',
    'DEBUG': False,
    'SOURCES': {},
    'SOURCES_DIR': os.path.join(here, 'data/sources'),
    'FEEDS': {},
    'UA_FILE': os.path.join(here, 'data/user_agent_strings.json'),
    'STATIONS_MAP_DIR': os.path.join(here, 'data/stations'),
}


def load_logging():
    # set log file name
    settings['LOGGING']['handlers']['info_file_handler']['filename'] = \
        settings['LOGFILE']
    # log to console if debug configured
    if settings['DEBUG']:
        settings['LOGGING']['loggers']['']['handlers'].append('console')
        settings['LOGGING']['root']['handlers'].append('console')
    logging.config.dictConfig(settings['LOGGING'])


# settings magic
okq_confmod = os.getenv('OKQ_CONFMODULE')
try:
    config = import_module(okq_confmod)
    local_settings = config.settings
except ImportError:
    local_settings = {}
    if okq_confmod != CONFMODULE:
        sys.stderr.write('No such configuration file ({})\n'
                         .format(os.environ.get('OKQ_CONFMODULE')))

settings = {}
# use default values or the values found in settings file
for setting in global_settings:
    settings[setting] = local_settings.get(setting,
                                           global_settings[setting])

# create logger instance
logger = logging.getLogger('okq')
try:
    load_logging()
except ValueError:
    raise ConfigError('Invalid logging configuration')

# check for existence and readability of UA_FILE;
# catch ConfigError as early as possible
try:
    open(settings['UA_FILE'], 'r')
except IOError as e:
    raise ConfigError("{} ({})"
                      .format(e.strerror, settings['UA_FILE']))

# check for existence of sources and stations map directory
for fname in ['STATIONS_MAP_DIR', 'SOURCES_DIR']:
    fpath = settings[fname]
    if not os.path.exists(fpath):
        raise ConfigError("Directory not found ({}: {})"
                          .format(fname, fpath))

# load sources from sources directory
settings['SOURCES'] = load_tree(settings['SOURCES_DIR'], dig_loader)
if not settings['SOURCES']:
    raise SourceError("No configured source")

# load status db
statusdb = create_statusdb(settings['DATABASES']['status'])

# load records db
recsdb = create_recsdb(settings['DATABASES']['records'])

# create instance of cache and catch any error as early as possible
from .cache import FileCache
file_cache = FileCache(settings['CACHE'])
