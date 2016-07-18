# -*- coding: utf-8 -*-

from ..utils import load_backend


class BaseStatusWrapper(object):
    """Base wrapper class to get database status. This class is to be used
    as parent of any database status wrapper class.

    The children wrapper classes will have to define custom methods for
    creating the database connection.
    """

    def __init__(self, db_settings, *args, **kwargs):
        self._cnx = self.create_cnx(db_settings)

    def create_cnx(self, db_settings):
        """Create a connection to the database.

        .. warning:: This method has to be overwritten

        :param db_settings: dictionary containing database configuration
        :type db_settings: dict
        """
        raise NotImplementedError

    def db_init(self):
        """Initialize database.

        .. warning:: This method has be overwritten
        """
        raise NotImplementedError

    def set_status(self, name, data):
        """Save the status.

        .. warning:: This method has to be overwritten
        """
        raise NotImplementedError

    def get_status(self, name):
        """Return the status with the given name and arguments.

        .. warning:: This method has to be overwritten

        :param name: the name as found in `settings.SOURCES`
        :type name: str
        """
        raise NotImplementedError


def create_statusdb(db_settings):
    """Create a status database instance given a database settings dict."""
    status_db_mod = load_backend(db_settings['ENGINE'])
    return status_db_mod.StatusWrapper(db_settings)
