# -*- coding: utf-8 -*-

import json
import redis

from .base import BaseStatusWrapper

_PASSWORD = 'admin'
_HOST = 'localhost'
_PORT = '6379'
_DB_ID = 0

_STATUS_KEY = "okq_status:{name}"


class StatusWrapper(BaseStatusWrapper):
    """A wrapper for redis connection and custom methods"""

    def create_cnx(self, db_settings):
        """Create a connection to database.

        :param db_settings: dictionary containing database configuration
        :type db_settings: dict
        """
        return redis.StrictRedis(password=db_settings.get('PASSWORD', _PASSWORD),
                                 host=db_settings.get('HOST', _HOST),
                                 port=db_settings.get('PORT', _PORT),
                                 db=db_settings.get('DB_ID', _DB_ID))

    def db_init(self):
        pass

    def set_status(self, name, data):
        """Save the status in a redis list.

        Data is serialized in json
        """
        self._cnx.set(_STATUS_KEY.format(name=name), json.dumps(data))

    def get_status(self, name):
        """return the redis key with the given name and arguments.

        :param name: the name as found in `settings.SOURCES`
        :type name: str
        """
        return json.loads(self._cnx.get(_STATUS_KEY.format(name=name)))
