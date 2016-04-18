# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from .sqlalch import SQLAlchemyRecordsWrapper

from sqlalchemy.engine.url import URL

_NAME = 'openkongqi'


class RecordsWrapper(SQLAlchemyRecordsWrapper):

    def create_dsn(self, settings):
        engine = 'sqlite'
        db_name = '{}.db'.format(settings.get('NAME', _NAME))
        if db_name:
            dsn = URL(engine, database=db_name)
        else:  # empty string or None
            dsn = URL(engine)  # in memory sqlite db
        return dsn
