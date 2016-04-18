# -*- coding: utf-8 -*-

from copy import copy
from importlib import import_module
import os
import unittest

from openkongqi.conf import settings
from openkongqi.stations import get_station_map


here = os.path.abspath(os.path.dirname(__file__))
TEST_DATA_PATH = os.path.join(here, 'data')


class TestExtract(unittest.TestCase):

    def setUp(self):
        sources = copy(settings['SOURCES'])
        for src in sources:
            sources[src]['content-fpath'] = \
                os.path.join(TEST_DATA_PATH, '{}.html'.format(src))
        self.sources = sources


class TestExtractPM25in(TestExtract):

    def setUp(self):
        TestExtract.setUp(self)
        self.sources = {
            src: metadata
            for src, metadata in self.sources.items()
            if metadata['modname'] == 'pm25in'
        }
        self.mod = import_module('.' + 'pm25in', 'openkongqi.source')

    def test_numeric_integer(self):
        src_name = 'pm25.in/shanghai'
        src = self.mod.Source(src_name)
        data_points = src.extract(
            open(self.sources[src_name]['content-fpath'], 'rt').read()
        )
        # int value for pm2.5
        self.assertEqual(data_points[0][3], '33')

    def test_numeric_float(self):
        src_name = 'pm25.in/shanghai'
        src = self.mod.Source(src_name)
        data_points = src.extract(
            open(self.sources[src_name]['content-fpath'], 'rt').read()
        )
        # float values for CO
        self.assertEqual(data_points[2][3], '0.579')
