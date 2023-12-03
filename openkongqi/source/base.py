# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals
from datetime import datetime
import io
import logging
import os
import re
from urllib3.util.retry import Retry
from urllib3.exceptions import MaxRetryError

from celery.utils.log import get_task_logger
import requests

from ..apikeys import get_api_key
from ..conf import settings, statusdb, recsdb, file_cache
from ..exceptions import SourceError
from ..stations import get_station_map
from ..utils import get_rnd_item, get_uuid

import pytz


logger = get_task_logger(__name__)


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
        self._api_key = get_api_key(name.split(":")[0])
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

        .. note:: This is not performing any recursive search in the map
        """
        return get_uuid(settings['SOURCES'][self.name]['uuid'],
                        self._station_map[name]['uuid'])

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
        self.log_info("Cached {} kilobytes to server."
                    .format(os.path.getsize(fp)))
        return open(fp, 'rb')

    def pythonify(self, text, is_num=False):
        if text is None:
            return None

        if self.null_re is not None:
            if self.null_re.match(text) is None:
                if is_num:  # remove everything but nums and dots
                    try:
                        return float(re.sub(r'[^\d.]+', '', text))
                    except ValueError:
                        self.log_error(f"{self.name} - Could not convert value: {text}")
                else:
                    return text
            else:
                return None
        else:
            if is_num:  # remove everything but nums and dots
                try:
                    return float(re.sub(r'[^\d.]+', '', text))
                except ValueError:
                    self.log_error(f"{self.name} - Could not convert value: {text}")
            else:
                return text

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

    def log_debug(self, msg, *args, **kwargs):
        self.log(logging.DEBUG, msg, *args, **kwargs)

    def log_info(self, msg, *args, **kwargs):
        self.log(logging.INFO, msg, *args, **kwargs)

    def log_warning(self, msg, *args, **kwargs):
        self.log(logging.WARNING, msg, *args, **kwargs)

    def log_error(self, msg, *args, **kwargs):
        self.log(logging.ERROR, msg, *args, **kwargs)

    def log_critical(self, msg, *args, **kwargs):
        self.log(logging.CRITICAL, msg, *args, **kwargs)

    def log(self, level, msg, *args, **kwargs):
        _msg = "{} - {}".format(self.name, msg)
        logger.log(level, _msg, *args, **kwargs)


class HTTPSource(BaseSource):

    #: default HTTP method to use when performing the request
    method='GET'
    #: HTTP request timeout value in second
    http_timeout = 10
    #: SSL Verification
    ssl_verify = True


    def __init__(self, name):
        super(HTTPSource, self).__init__(name)

    def fetch(self):
        req = self.get_req()
        res = self.send(req)

        if res is None:
            self._info = None
            self._statuscode = None
            return None

        self._info = res.headers
        self._statuscode = res.status_code

        try:
            # don't use `resp.headers.get('content-length`)
            # because if it doesn't exist in headers it will return None
            # which makes it a false negative
            content_length = res.headers['content-length']
        except KeyError:
            pass
        else:
            if (self._statuscode == 200 and content_length == '0'):
                self.log_warning("Fetched content is empty; skipping cache ...")
                return None

        return self.post_fetch(res)

    def send(self, req, timeout=None):
        """Wrap a :class:`Request <requests.Request>` in a session and send it.
        Any type of error (status code not 2xx or exceptions) will be handled here
        and the function then returns ``None``.

        :param req: :class:`Request <requests.Request>` instance
        :type req: requests.Request
        :param timeout: (optional) How long to wait for the server to send data
            before giving up
        :type timeout: float or tuple
        :rtype: requests.Response
        """
        if req.url is None:
            self.log_warning("no URL provided, abort fetch")
            return None

        if timeout is None:
            timeout = self.http_timeout

        retry_count = 3
        retry_strategy = Retry(
            total=retry_count,
            status_forcelist=[413, 429, 500, 502, 503, 504],
        )
        adapter = requests.adapters.HTTPAdapter(max_retries=retry_strategy)
        s = requests.Session()
        s.mount("https://", adapter)
        s.mount("http://", adapter)

        s = requests.Session()
        prepped = s.prepare_request(req)

        try:
            res = s.send(prepped, timeout=timeout, verify=self.ssl_verify)
        except MaxRetryError:
            self.log_error("fetch failed after {} retries".format(retry_count))
            return None
        except requests.Timeout as e:
            self.log_error("fetch error: timeout ({})".format(e.request.url))
            return None
        except requests.RequestException as e:
            self.log_error("fetch error: {}".format(e.request.url))
            return None

        if res.status_code != requests.codes.ok:
            self.log_error("fetch error: status {} ({})".format(
                    res.status_code,
                    req.url,
                )
            )
            self.log_debug(res.text)
            return

        s.close()

        self.log_info("fetch success: {}".format(res.status_code))
        self.log_debug(res.text)

        return res

    def post_fetch(self, response):
        # The Bytes stream is required for the caching operations
        # response.content is a bytes string
        return io.BytesIO(response.content)

    def get_req(self, **kwargs):
        """Return an :class:`requests.Request` instance
        """
        req = requests.Request(
            self.method,
            self.get_url(**kwargs),
            data=self.get_data(**kwargs),
            json=self.get_json(**kwargs),
            params=self.get_params(**kwargs),
            headers=self.get_headers(**kwargs),
        )
        return req

    def get_url(self, **kwargs):
        """Return the target URL, if ``None`` is returned, the scrape will be
        gracefully stopped.
        """
        return self.target

    def get_data(self, **kwargs):
        return {}

    def get_json(self, **kwargs):
        return None

    def get_params(self, **kwargs):
        return {}

    def get_headers(self, **kwargs):
        headers = {
            'User-Agent': get_rnd_item(settings['UA_FILE']),
        }
        return headers

    def get_status_data(self):
        data = {
            'code': self._statuscode
        }
        if self._info is not None and 'Last-Modified' in self._info:
            data['last-modified'] = self._info['Last-Modified']
        return data
