# -*- coding: utf-8 -*-

from .sqlalch import SQLAlchemyRecordsWrapper

from sqlalchemy.engine.url import URL

_NAME = 'openkongqi'
_USERNAME = 'admin'
_PASSWORD = 'admin'
_HOST = 'localhost'
_PORT = '8080'
_DRIVER = ''


class RecordsWrapper(SQLAlchemyRecordsWrapper):

    def create_dsn(self, settings):
        engine = 'mysql'
        driver = settings.get('DRIVER', _DRIVER)
        if driver:
            engine += "+{}".format(driver)
        dsn = URL(engine,
                  username=settings.get('USERNAME', _USERNAME),
                  password=settings.get('PASSWORD', _PASSWORD),
                  host=settings.get('HOST', _HOST),
                  port=settings.get('PORT', _PORT),
                  database=settings.get('NAME', _NAME))
        return dsn
