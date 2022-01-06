# -*- coding: utf-8 -*-
"""
Naive settings for openkongqi

Very naive approach for settings management. 

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
from .cache.base import create_cachedb


here = os.path.abspath(os.path.dirname(__file__))

#CONFMODULE = 'okqconfig'
#os.environ.setdefault('OKQ_CONFMODULE', CONFMODULE)

# default settings
global_settings = {
    'RESOURCE_CACHE': '_cache',
    'DATABASES': {
        'status': {
            'ENGINE': 'openkongqi.status.redisdb',
            'HOST': 'localhost',
            'PORT': 6379,
            'DB_ID': 1,
        },
        'records': {
            'ENGINE': 'openkongqi.records.sqlite3',
            'NAME': 'openkongqi',
        },
        'cache': {
            'ENGINE': 'openkongqi.cache.redisdb',
            'HOST': 'localhost',
            'PORT': 6379,
            'DB_ID': 0,
        },
    },
    'DEBUG': False,
    'SOURCES': {},
    'SOURCES_DIR': os.path.join(here, 'data/sources'),
    'FEEDS': {},
    'UA_FILE': os.path.join(here, 'data/user_agent_strings.json'),
    'STATIONS_MAP_DIR': os.path.join(here, 'data/stations'),
    'API_KEYS': {}
}

settings = {}
statusdb = None
cachedb = None
recsdb = None
file_cache = None


def config_from_object(obj):
    global statusdb, cachedb, recsdb, file_cache
    local_settings = obj.settings
    # use default values or the values found in settings file
    for setting in global_settings:
        settings[setting] = local_settings.get(setting,
                global_settings[setting])

    # check for existence and readability of UA_FILE;
    # catch ConfigError as early as possible
    try:
        with open(settings['UA_FILE'], 'r'):
            pass
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

    # load cache db
    cachedb = create_cachedb(settings['DATABASES']['cache'])

    # load records db
    recsdb = create_recsdb(settings['DATABASES']['records'], cachedb)

    # create instance of cache and catch any error as early as possible
    from .filecache import FileCache
    file_cache = FileCache(settings['RESOURCE_CACHE'])
