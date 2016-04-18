# -*- coding: utf-8 -*-

from ..utils import load_backend


class BaseRecordsWrapper(object):
    """Base wrapper class to get database records. This class is to be used
    as parent of any database records wrapper class.

    The children wrapper class will have to define custom methods,
    for creating the database connection.
    """

    def __init__(self, settings, *args, **kwargs):
        self._cnx = self.create_cnx(settings)

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

        Check if the combination timestamp, uuid already exists in the db.

        .. warning:: This method has be overwritten

        :param record: a tuple to be appended to the db as a single row
        :type record: tuple
        """
        raise NotImplementedError

    def write_record(self, record, commit=True):
        """Save a single record.

        .. warning:: This method has to be overwritten

        :param record: a tuple to be appended to the db as a single row
        :type record: tuple
        :param commit: boolean for updating db
        :type commit: bool
        """
        raise NotImplementedError

    def write_records(self, records):
        """Save the records

        .. warning:: This method has to be overwritten

        :param records: list of tuples to be appended to the db as rows
        :type records: list of tuples
        """
        raise NotImplementedError

    def get_records(self, start, end, filters=None):
        """Returns a list of Records.

        .. warning:: This method has to be overwritten

        :param start: the start date (lower boundary)
        :param end: the end date (upper boundary)
        :param filters: list of columns to select
        :type filters: list of str
        """
        raise NotImplementedError


def create_recsdb(settings):
    mod = load_backend(settings['ENGINE'])
    return mod.RecordsWrapper(settings)
