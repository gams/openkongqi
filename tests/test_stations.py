# -*- coding: utf-8 -*-
import os
import unittest

from openkongqi.conf import config_from_object
from openkongqi.utils import get_uuid


here = os.path.abspath(os.path.dirname(__file__))
TEST_DATA_PATH = os.path.join(here, 'data', 'stations')


# Adding configuration before importing get_station_map from stations
# to override the STATIONS_MAP_DIR for production data with test data path
class Conf(object):
    settings = {
        'STATIONS_MAP_DIR': TEST_DATA_PATH
    }

confobj = Conf()
config_from_object(confobj)

from openkongqi.stations import get_station_map


class TestStations(unittest.TestCase):
    """Test the stations UUID map functions"""

    def test_get_uuid(self):
        """Test UUID generation"""
        self.assertEqual(
            get_uuid('cn', 'shanghai', 'jinganjincezhan'),
            'cn:shanghai:jinganjincezhan')
        self.assertEqual(
            get_uuid('cn:shanghai', 'jinganjincezhan'),
            'cn:shanghai:jinganjincezhan')

    def test_get_stations_uuid(self):
        """Test station map generation"""
        self.assertEqual(
            get_station_map('us:oh'),
            {
                'Cleveland Station': {
                    'uuid': 'cleveland'
                },
                'Cincinnati Station': {
                    'uuid': 'cincinnati'
                }
            }
        )

    def test_get_stations_uuid_wildcard(self):
        self.assertEqual(
            get_station_map('us:*'),
            {
                'Cleveland Station': {
                    'uuid': 'cleveland'
                },
                'Cincinnati Station': {
                    'uuid': 'cincinnati'
                },
                'San Francisco Station': {
                    'uuid': 'san_francisco'
                },
                'Los Angeles Station': {
                    'uuid': 'los_angeles'
                }
            }
        )

    def test_get_stations_uuid_dne(self):
        self.assertEqual(
            get_station_map('us:na'),
            {}
        )

    def test_get_stations_uuid_wildcard_dne(self):
        self.assertEqual(
            get_station_map('mx:*'),
            {}
        )
