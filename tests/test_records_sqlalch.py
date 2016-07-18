# -*- coding: utf-8 -*-

import unittest

from datetime import datetime
from importlib import import_module
from uuid import uuid4
import os
import pytz

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
        records = mod.DATA
        context = {'modname': mod.MODNAME}
        return {
            'key_context': context,
            'records': records,
        }


class TestWriteRecords(TestRecordsWrapper):

    def test_write_records(self):
        data = self.load_data('pm25in_sh_201607130254_201607130454')
        records = data['records']
        context = data.get('key_context')
        # we only need to test for one uuid
        uuid = 'cn:shanghai:putuo'
        putuo_records = records[uuid]
        # insert the last two hours
        start = datetime(2016, 7, 13, 3, tzinfo=pytz.utc)  # 03:54 and 04:54
        # stop = datetime(2016, 7, 14)
        last_records = filter(lambda r: r['ts'] > start, putuo_records)
        self.wrapper.write_records({uuid: last_records},
                                   ignore_check_latest=False,
                                   context=context)
        # should be 04:54
        self.assertEqual(
            self.wrapper.get_latest(uuid, context=context),
            last_records[-1]
        )
        # insert the first hour, check that latest is not overwritten
        first_records = filter(lambda r: r['ts'] < start, putuo_records)
        self.wrapper.write_records({uuid: first_records},
                                   ignore_check_latest=True,
                                   context=context)
        # check that latest is still 04:54
        self.assertEqual(
            self.wrapper.get_latest(uuid, context=context),
            last_records[-1]
        )
        # check that inserting existing data would not raise exceptions
        try:
            self.wrapper.write_records({uuid: putuo_records}, context=context)
        except:
            self.fail(
                'Attemtping to insert duplicate records should not raise exceptions!'
            )


class TestGetRecords(TestRecordsWrapper):

    def test_get_records(self):
        data = self.load_data('pm25in_sh_201607130254_201607130454')
        records = data['records']
        self.wrapper.write_records(records,
                                   ignore_check_latest=False,
                                   context=data.get('key_context'))
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
            records[station_uuid][-1]['fields']['pm25']
        )
