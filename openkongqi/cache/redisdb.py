# -*- coding: utf-8 -*-

import redis

from .base import BaseCacheWrapper

# default redis settings
_HOST = 'localhost'
_PORT = '6379'
_DB_ID = 0


class CacheWrapper(BaseCacheWrapper):

    def create_cnx(self, db_settings):
        return redis.StrictRedis(host=db_settings.get('HOST', _HOST),
                                 port=db_settings.get('PORT', _PORT),
                                 db=db_settings.get('DB_ID', _DB_ID))

    def set(self, key, value):
        return self._cnx.set(key, value)

    def get(self, key):
        return self._cnx.get(key)
