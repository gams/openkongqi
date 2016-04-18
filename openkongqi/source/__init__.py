# -*- coding: utf-8 -*-

from ..conf import settings


def get_source(name):
    """Return a single source information.

    :param name: source name as used in the configuration
    :type name: str
    :returns: info - a dict of information about this source
    """
    info = settings['SOURCES'][name]
    info['name'] = name
    return info


def get_sources():
    """Return a generator going over the sources and returning source info.

    :returns: generator - sources information
    """
    for name in settings['SOURCES'].keys():
        yield get_source(name)
