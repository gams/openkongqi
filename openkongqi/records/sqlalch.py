# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals
import pytz

import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy import Column, String, DateTime, Float
from sqlalchemy.orm import scoped_session, sessionmaker, load_only
from sqlalchemy.ext.declarative import declarative_base

from .base import BaseRecordsWrapper

Base = declarative_base()


class SQLAlchemyRecordsWrapper(BaseRecordsWrapper):

    def __init__(self, settings, *args, **kwargs):
        self._engine = create_engine(self.create_dsn(settings))
        super(SQLAlchemyRecordsWrapper, self).__init__(
            settings, *args, **kwargs
        )

    def create_dsn(self, settings):
        """Create a data source name (DNS) given a settings dict.

        .. warning:: This method has to be overwritten

        :returns: sqlalchemy.engine.url.URL instance
        """
        raise NotImplementedError

    def create_cnx(self, settings):
        db_session = scoped_session(sessionmaker(autocommit=False,
                                                 autoflush=False,
                                                 bind=self.get_engine()))
        return db_session

    def db_init(self):
        Base.metadata.create_all(bind=self.get_engine())

    def is_duplicate(self, record):
        dup_count = self._cnx.query(Record).filter_by(
            ts=record[0].astimezone(pytz.utc),
            uuid=record[1]
        ).count()
        return (not dup_count == 0)

    def get_engine(self):
        """Return engine url / data source name (DSN) of database."""
        return self._engine

    def write_record(self, record, commit=True):
        if not self.is_duplicate(record):
            r = Record.from_tuple(record)
            self._cnx.add(r)
            if commit:
                self._cnx.commit()

    def write_records(self, records, commit_size=100):
        # first map through list to convert to
        # SQLAlchemy objects to be ready to committed to DB
        recs = map(lambda r: Record.from_tuple(r),
                   records)
        try:  # the fastest way
            self._cnx.add_all(recs)
            self._cnx.commit()
        except sqlalchemy.exc.IntegrityError:
            # first rollback to restart session
            self._cnx.rollback()
            # split records into chunks of given size
            # the size of the last chunk is the remainder left
            row_chunks = [recs[i:i + commit_size]
                          for i in range(0, len(recs), commit_size)]
            for chunk in row_chunks:
                try:
                    self._cnx.add_all(chunk)
                    self._cnx.commit()
                except sqlalchemy.exc.IntegrityError:
                    # resort to committing one by one
                    self._cnx.rollback()  # restart session
                    for rec in chunk:
                        rec = Record.to_tuple(rec)
                        self.write_record(rec, commit=True)

    def get_records(self, start, end, filters=None):
        query = self._cnx.query(Record)
        if filters is not None:
            # NOTE: `load_only`` is only available in >=0.9.0
            query = query.options(load_only(*filters))
        # time boundaries
        query = query.filter(Record.ts >= start and Record.ts <= end)
        return query


class Record(Base):
    __tablename__ = 'records'

    ts = Column(DateTime, primary_key=True)
    uuid = Column(String(250), nullable=False, primary_key=True)
    key = Column(String(250), nullable=False, primary_key=True)
    value = Column(Float(), nullable=True)

    def __repr__(self):
        return (
            "<Record(ts='{ts}', uuid='{uuid}', key='{key}', value='{value}')>"
            .format(ts=self.ts, uuid=self.uuid, key=self.key, value=self.value)
        )

    @classmethod
    def from_tuple(self, record):
        """Return `Record` object from a tuple.

        The indices of `record` should correspond to the following criteria:
            0 - datetime.datetime object with timezone information
            1 - uuid key
            2 - string indicating type of pollutant
            3 - value of the pollutant

        :returns: openkongqi.records.sqlalch.Record
        """
        return Record(
            ts=record[0].astimezone(pytz.utc),  # UTC tz
            uuid=record[1],
            key=record[2],
            value=record[3]
        )

    @classmethod
    def to_tuple(self, record):
        """Return a tuple from a `Record` object.

        .. note:: Inverse function of `Record.from_tuple`

        The tuple returned should have the same data structure as
        the `record` parameter passed to `Record.from_tuple`.

        :returns: tuple
        """
        return (
            record.ts,
            record.uuid,
            record.key,
            record.value,
        )
