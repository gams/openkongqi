# -*- coding: utf-8 -*-
from datetime import datetime
import json
import pytz

from ..utils import load_backend

_CACHE_KEY = 'okq:{moduuid}:{uuid}:latest'


class BaseRecordsWrapper(object):
    """Base wrapper class to get database records. This class is to be used
    as parent of any database records wrapper class.

    The children wrapper class will have to define custom methods,
    for creating the database connection.
    """

    ts_fmt = "%Y-%m-%dT%H:%M:%SZ"

    def __init__(self, settings, cache, *args, **kwargs):
        self._cnx = self.create_cnx(settings)
        self._cache = cache
        # NOTE: can't apply key context here
        # because it hasn't been set when this is initialized
        self._cache_key = settings.get('CACHE_KEY', _CACHE_KEY)

    def create_cnx(self, settings):
        """Create a connection to the database

        .. warning:: This method has be overwritten
        """
        raise NotImplementedError

    def db_init(self):
        """Initialize database.

        .. warning:: This method has be overwritten
        """
        raise NotImplementedError

    def is_duplicate(self, record):
        """Check for duplicated records.

        Check if the timestamp, uuid, key already exists in the db.
        Note that these are all the primary keys.

        .. warning:: This method has be overwritten
        """
        raise NotImplementedError

    def write_records(self, records, ignore_check_latest=False, context=None):
        """Save the records

        See data extraction format on what to expect as input.

        .. warning:: This method has to be overwritten
        """
        raise NotImplementedError

    def get_records(self, start, end, filters=None, context=None):
        """Returns a list of Records.

        .. warning:: This method has to be overwritten

        :param start: the start date (lower boundary)
        :param end: the end date (upper boundary)
        :param filters: list of columns to select
        :type filters: list of str
        """
        raise NotImplementedError

    def _get_cache_key(self, uuid, context=None):
        ctx_fmt = {u'uuid': uuid}
        if context is not None:
            ctx_fmt.update(context)
        return self._cache_key.format(**ctx_fmt)

    def set_latest(self, uuid, record, context=None):
        """Set record as the latest entry in cache database.

        :param uuid: unique id
        :type uuid: str
        """
        latest_record = {
            'ts': self._ts_to_string(record['ts']),
            'fields': record['fields'],
        }
        latest_json = json.dumps(latest_record)
        key = self._get_cache_key(uuid=uuid, context=context)
        self._cache.set(key, latest_json)

    def get_latest(self, uuid, context=None):
        """Get latest record entry from cache database.

        :param uuid: unique id
        :type uuid: str
        """
        latest = self._cache.get(
            self._get_cache_key(uuid=uuid, context=context)
        )
        if latest is None:
            return None
        record = json.loads(latest)
        return {
            'ts': self._string_to_ts(record['ts']),
            'fields': record['fields'],
        }

    def _ts_to_string(self, ts):
        """Convert a datetime.datetime object to a string.

        This is done for compatibility in serialization.

        Format:    %Y-%m-%dT%H:%M:%SZ
        Example: 2016-07-13T10:09:56Z

        :param ts: timestamp
        :type ts: datetime.datetime
        """
        # remove the microseconds
        ts = ts.replace(microsecond=0)
        # convert to UTC or keep naive
        if ts.tzinfo is not None:
            ts = ts.astimezone(pytz.utc)
        return datetime.strftime(ts, self.ts_fmt)

    def _string_to_ts(self, ts_string):
        """Convert a timestamp string to datetime.datetime object.

        The input format has to be the same
        from the output of ``_ts_to_string``.

        :param ts_string: timestamp string
        :type ts_string: str
        """
        return datetime \
            .strptime(ts_string, self.ts_fmt) \
            .replace(tzinfo=pytz.utc)


def create_recsdb(settings, cache):
    mod = load_backend(settings['ENGINE'])
    return mod.RecordsWrapper(settings, cache)
