# -*- coding: utf-8 -*-

import httpretty
import unittest
from importlib import import_module

from openkongqi.conf import config_from_object, settings


class emptyConf(object):
    settings = {}


class TestFetch(unittest.TestCase):

    def setUp(self):
        confobj = emptyConf()
        config_from_object(confobj)
        mod = import_module('openkongqi.source.' + 'pm25in')
        src_name = 'pm25.in:shanghai'
        self.src = mod.Source(src_name)

    def tearDown(self):
        httpretty.disable()
        httpretty.reset()

    @httpretty.activate
    def test_nonempty_resp_with_0_content_length(self):
        """Return none because content length is 0"""
        url = "http://nonempty-resp-with-0-content-length.com"
        httpretty.register_uri(
            httpretty.GET, url,
            body="This is NOT an empty response",
            status=200,
            content_type="text/html; charset=UTF-8",
            forcing_headers={
                'content-length': '0'
            }
        )

        self.src.target = url
        self.assertIsNone(self.src.fetch())

    @httpretty.activate
    def test_nonempty_resp_with_no_headers(self):
        """Still return response because of potential false negative"""
        url = "http://nonempty-resp-without-headers.com"
        httpretty.register_uri(
            httpretty.GET, url,
            body="This is NOT an empty response",
            status=200,
            content_type="text/html; charset=UTF-8",
            forcing_headers={}
        )

        self.src.target = url
        self.assertIsNotNone(self.src.fetch())
        self.assertEqual(self.src.fetch().read(),
                         b"This is NOT an empty response")

    @httpretty.activate
    def test_empty_resp(self):
        """Empty response returns content-length of 0"""
        url = "http://empty-resp.com"
        httpretty.register_uri(
            httpretty.GET, url,
            body="",
            status=200,
        )

        self.src.target = url
        self.assertIsNone(self.src.fetch())
