# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals
from datetime import datetime
from inspect import getmodulename
import logging
import os
import re
import socket
import ssl
import urllib2

from ..conf import settings, logger, statusdb, recsdb, file_cache
from ..exceptions import SourceError
from ..stations import get_station_map
from ..utils import get_rnd_item, get_uuid

import pytz


HTTP_TIMEOUT = 10

logger = logging.getLogger("openkongqi.source.{}"
                           .format(getmodulename(__file__)))


class BaseSource(object):
    """Base source class to scrape online resources. This class is to be used
    as parent of any scraping class.

    Basic mechanism from fetching online resource to hosing extracted data in
    the database, :meth:`openkongqi.source.BaseSource.scrape` is the main entry
    point of this class.
    """

    key_context = None
    _now = None

    def __init__(self, name):
        """
        :param name: fetch name
        :type name: str
        """
        if name not in settings['SOURCES']:
            raise SourceError('Unknown source ({})'.format(name))
        self.name = name
        self.target = settings['SOURCES'][name]['target']
        self._station_map = get_station_map(
            settings['SOURCES'][name]['uuid'])
        self._tz = pytz.timezone(settings['SOURCES'][name]['tz'])
        self._status = statusdb
        self._cache = file_cache
        self._records = recsdb

    def scrape(self):
        """Main entry point for :class:`openkongqi.source.BaseSource` instances.

        Orchestrates the resource scraping, following actions are performed:

        * :meth:`openkongqi.source.BaseSource.fetch`: fetch online resource
        * :meth:`openkongqi.source.BaseSource.save_status`: save fetching
          status
        * :meth:`openkongqi.source.BaseSource.cache`: save the resource in the
          cache
        * :meth:`openkongqi.source.BaseSource.extract`: extract the data
          from the resource
        * :meth:`openkongqi.source.BaseSource.save_data`: save extracted data
        """
        self._now = datetime.now(pytz.utc)
        src_content = self.fetch()
        self.save_status()
        if src_content is not None:
            content = self.cache(src_content)
            data = self.extract(content)
            self.save_data(data)

    def fetch(self):
        """Fetch the resource

        .. warning:: This method has to be overwritten

        :returns: content - a file-like object
        """
        raise NotImplementedError

    def post_fetch(self, resource):
        """Treat the resource after fetching raw content

        .. warning:: This method has to be overwritten

        :param resource: raw content / data (could be http, csv, xml, etc...)
        :returns: content - a file-like object
        """
        raise NotImplementedError

    def get_station_uuid(self, name):
        """Return the uuid of a station

        .. warning:: This is not performing any recursive search in the map
        """
        return get_uuid(settings['SOURCES'][self.name]['uuid'],
                        self._station_map[name])

    def get_status_data(self):
        """Get the fetch status

        :returns: data - a dict with data to serialize in the status entry
        """
        return dict()

    def save_status(self):
        """Save status data to keep track of fetching history.

        Uses :meth:`openkongqi.source.BaseSource.get_status_data` to get the
        status data to save.
        """
        data = self.get_status_data()
        if data is None:
            data = {'ts': self._now.strftime('%Y%m%d%H%M%S')}
        else:
            data.setdefault('ts', self._now.strftime('%Y%m%d%H%M%S'))
        self._status.set_status(self.name, data)

    def cache(self, content):
        """Cache fetching content

        :param content: content to cache
        :type content: file-like object
        """
        self._cache.set(self.name, content, self._now)
        fp = self._cache.get_fp(self.name, self._now)
        # display how much is cached into server
        logger.info("Cached {} kilobytes to server."
                    .format(os.path.getsize(fp)))
        return open(fp, 'r')

    def pythonify(self, text, is_num=False):
        if text is None:
            return None
        if self.null_re is not None:
            if self.null_re.match(text) is None:
                if is_num:  # remove everything but nums and dots
                    return re.sub(r'[^\d.]+', '', text)
                else:
                    return text
            else:
                return None

    def extract(self, content):
        """Extract data from the content
        """
        raise NotImplementedError

    def save_data(self, data, ignore_check_latest=False):
        self._records.write_records(data,
                                    ignore_check_latest=ignore_check_latest,
                                    context=self.key_context)

    def get_latest(self, uuid):
        return self._records.get_latest(uuid, context=self.key_context)

    def get_records(self, uuid, start, end, filters=None):
        return self._records.get_records(uuid=uuid,
                                         start=start,
                                         end=end,
                                         context=self.key_context)


class HTTPSource(BaseSource):

    def __init__(self, name):
        super(HTTPSource, self).__init__(name)

    def fetch(self):

        _common_error_header = "Data fetch failure"

        try:
            req = self.get_req(self.target)
            resp = urllib2.urlopen(req, timeout=HTTP_TIMEOUT)
        except urllib2.HTTPError as e:
            self._info = None
            self._statuscode = e.code
            logger.error("{}: {} {} ({})"
                         .format(_common_error_header,
                                 e.code, e.msg, e.url))
            return None
        except urllib2.URLError as e:
            if isinstance(e.reason, socket.timeout):
                self._info = None
                self._statuscode = 418
                logger.error("{}: HTTP Timeout".format(_common_error_header))
                return None
            else:
                self._info = None
                self._statuscode = None
                logger.error("{}: {}"
                             .format(_common_error_header, e.reason.strerror))
                return None
        except socket.timeout:
            self._info = None
            self._statuscode = 418
            logger.error("{}: HTTP Timeout".format(_common_error_header))
            return None
        except ssl.CertificateError as e:
            logger.error("{}: {}"
                         .format(_common_error_header, e.message))
            return None

        self._info = resp.info()
        self._statuscode = resp.getcode()
        logger.debug("Fetch status: HTTP {}".format(self._statuscode))

        if self._statuscode == 204:  # 204: No Content
            logger.warning("No message body included")
            return None

        try:
            # don't use `resp.headers.get('content-length`)
            # because if it doesn't exist in headers it will return None
            # which makes it a false negative
            content_length = resp.headers['content-length']
        except KeyError:
            pass
        else:
            if (self._statuscode == 200 and content_length == '0'):
                logger.warning("Fetched content is empty; skipping cache ...")
                return None

        return self.post_fetch(resp)

    def post_fetch(self, resource):
        return resource

    def get_req(self, target):
        """Return an :class:`urllib2.Request` instance
        """
        req = urllib2.Request(target)
        req.add_header('User-Agent', get_rnd_item(settings['UA_FILE']))
        return req

    def get_status_data(self):
        data = {
            'code': self._statuscode
        }
        if self._info is not None and 'Last-Modified' in self._info:
            data['last-modified'] = self._info['Last-Modified']
        return data
