# -*- coding: utf-8 -*-

import unittest

from openkongqi.utils import get_uuid


class TextStations(unittest.TestCase):
    """Test the stations UUID map functions"""
    def test_get_uuid(self):
        """test UUID generation"""
        self.assertEqual(
            get_uuid('cn', 'shanghai', 'jinganjincezhan'),
            'cn/shanghai/jinganjincezhan')
        self.assertEqual(
            get_uuid('cn/shanghai', 'jinganjincezhan'),
            'cn/shanghai/jinganjincezhan')
