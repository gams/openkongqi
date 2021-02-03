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
            get_uuid('cn', 'shanghai', 'jinganjiancezhan'),
            'cn:shanghai:jinganjiancezhan')
        self.assertEqual(
            get_uuid('cn:shanghai', 'jinganjiancezhan'),
            'cn:shanghai:jinganjiancezhan')

    def test_get_station_map_uuid(self):
        """Test generating a station map from a UUID representing a station JSON."""
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

    def test_get_station_map_wildcard(self):
        """Test generating a concatenated station map from a wildcarded UUID representing a folder of station JSONs."""
        self.assertEqual(
            get_station_map('us:*'),
            {
                'Cleveland Station': {
                    'uuid': 'oh:cleveland'
                },
                'Cincinnati Station': {
                    'uuid': 'oh:cincinnati'
                },
                'San Francisco Station': {
                    'uuid': 'ca:san_francisco'
                },
                'Los Angeles Station': {
                    'uuid': 'ca:los_angeles'
                }
            }
        )

    def test_get_station_map_uuid_wildcard(self):
        """Test generating station map from a redundantly wildcarded UUID representing a station JSON."""
        self.assertEqual(
            get_station_map('us:oh:*'),
            {
                'Cleveland Station': {
                    'uuid': 'cleveland'
                },
                'Cincinnati Station': {
                    'uuid': 'cincinnati'
                }
            }
        )

    def test_get_station_map_uuid_dne(self):
        """Test generating station map from a UUID representing a station JSON that doesn't exist."""
        self.assertEqual(
            get_station_map('us:xyz'),
            {}
        )

    def test_get_station_map_wildcard_empty(self):
        """Test generating station map from a wildcard UUID representing an empty folder."""
        self.assertEqual(
            get_station_map('mx:*'),
            {}
        )

    def test_get_station_map_uuid_wildcard_dne(self):
        """Test generating station map from a redundantly wildcarded UUID
         representing a station JSON that doesn't exist."""
        self.assertEqual(
            get_station_map('mx:abc:*'),
            {}
        )
