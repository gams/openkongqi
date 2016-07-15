# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from .sqlalch import SQLAlchemyRecordsWrapper

from sqlalchemy.engine.url import URL

_NAME = 'openkongqi'


class RecordsWrapper(SQLAlchemyRecordsWrapper):

    def create_dsn(self, settings):
        engine = 'sqlite'
        db_name = settings.get('NAME', _NAME)
        db_filename = '{}.db'.format(db_name)
        if db_name == ':memory:':
            dsn = URL(engine)  # in memory sqlite db
        else:
            dsn = URL(engine, database=db_filename)
        return dsn
