# -*- coding: utf-8 -*-

import unittest

from datetime import datetime
from importlib import import_module
from uuid import uuid4
import os

from openkongqi.cache.redisdb import CacheWrapper
from openkongqi.records.sqlite3 import RecordsWrapper


class TestRecordsWrapper(unittest.TestCase):
    """Test RecordsWrapper from openkongqi.records.sqlalch"""

    def setUp(self):
        self.dbname = ":memory:"  # in memory
        # create unique okqtest key prefix to prevent clashes
        self.test_key_prefix = 'okqtest:{}'.format(uuid4().hex)
        cache_key = self.test_key_prefix + ':{uuid}:latest'
        db_settings = {
            'records': {
                'NAME': self.dbname,
                'CACHE_KEY': cache_key,
            },
            'cache': {
                'HOST': 'localhost',
                'PORT': 6379,
                'DB_ID': 10,
            },
        }
        self.cache = CacheWrapper(db_settings['cache'])
        self.wrapper = RecordsWrapper(db_settings['records'], self.cache)
        self.wrapper.db_init()

    def tearDown(self):
        try:
            # just delete whole file first
            os.remove('{}.db'.format(self.dbname))
        except OSError:
            self.wrapper._cnx.execute("DROP TABLE records")
        # drop all redis keys
        self.cache._cnx.delete(
            *self.cache._cnx.keys('{}*'.format(self.test_key_prefix))
        )

    def load_data(self, filemod):
        """Load records in database, return the records"""
        mod = import_module('tests.data.' + filemod)
        recs = mod.DATA
        context = {'moduuid': mod.MODNAME}
        self.wrapper.write_records(recs, context=context)
        return {
            'key_context': context,
            'records': recs,
        }

    def test_get_records(self):
        data = self.load_data('pm25in_sh_201607130254_201607130454')
        recs = data['records']
        station_uuid = 'cn:shanghai:putuo'
        start = datetime(2016, 7, 13, 3)  # should query 03:54 and 04:54
        end = datetime(2016, 7, 14)
        res = self.wrapper.get_records(station_uuid, start, end,
                                       context=data.get('key_context'))
        res = list(res)
        # two different records for two timestamps
        self.assertEqual(len(res), 2)
        self.assertEqual(
            res[-1]['fields']['pm25'],
            recs[station_uuid][-1]['fields']['pm25']
        )
