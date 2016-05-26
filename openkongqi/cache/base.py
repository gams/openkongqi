# -*- coding: utf-8 -*-

from ..utils import load_backend


class BaseCacheWrapper(object):
    """A naive cache implementation with no data invalidation"""

    def __init__(self, db_settings, *args, **kwargs):
        self._cnx = self.create_cnx(db_settings)

    def create_cnx(self, db_settings):
        """Create a connection to the database.

        .. warning:: This method has to be overwritten
        """
        raise NotImplementedError

    def set(self, key, value):
        raise NotImplementedError

    def get(self, key):
        raise NotImplementedError


def create_cachedb(settings):
    mod = load_backend(settings['ENGINE'])
    return mod.CacheWrapper(settings)
