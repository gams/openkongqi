# -*- coding: utf-8 -*-

from copy import copy
from importlib import import_module
import os
import unittest

from openkongqi.conf import config_from_object, settings


here = os.path.abspath(os.path.dirname(__file__))
TEST_DATA_PATH = os.path.join(here, 'data')


class emptyConf(object):
    settings = {}


class TestExtract(unittest.TestCase):

    def setUp(self):
        confobj = emptyConf()
        config_from_object(confobj)
        sources = copy(settings['SOURCES'])
        for src in sources:
            sources[src]['content-fpath'] = \
                os.path.join(TEST_DATA_PATH, '{}.html'.format(
                    src.replace(':', os.sep)
                ))
        self.sources = sources


class TestExtractPM25in(TestExtract):

    def setUp(self):
        TestExtract.setUp(self)
        self.sources = {
            src: metadata
            for src, metadata in self.sources.items()
            if metadata['modname'].endswith('pm25in')
        }
        self.mod = import_module('openkongqi.source.' + 'pm25in')
        # shanghai covers most cases, can always override
        self.src_name = 'pm25.in:shanghai'
        self.src = self.mod.Source(self.src_name)
        with open(self.sources[self.src_name]['content-fpath'], 'rt') as fd:
            self.data_points = self.src.extract(
                fd.read()
            )

    def test_numeric_integer(self):
        # int value for pm2.5
        uuid = 'cn:shanghai:hongkou'
        self.assertIn(uuid, self.data_points)
        self.assertEqual(
            self.data_points[uuid][0]['fields']['pm25'],
            22.0
        )

    def test_numeric_float(self):
        # float values for CO
        uuid = 'cn:shanghai:putuo'
        self.assertIn(uuid, self.data_points)
        self.assertEqual(
            self.data_points[uuid][0]['fields']['co'],
            0.653
        )
