# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

from .conf import settings

_API_KEYS = settings['API_KEYS']


def get_api_key(provider=None):
    """Get the api key map, given a provider

    :param provider: a provider for the API Key
    :type provider: str|unicode
    """
    try:
        api_key = _API_KEYS[provider]
    except KeyError:
        return None
    return api_key
