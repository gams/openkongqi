# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals
import pytz

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
            r = Record(ts=record[0].astimezone(pytz.utc),  # UTC timezne
                       uuid=record[1],
                       key=record[2],
                       value=record[3])
            self._cnx.add(r)
        if commit:
            self._cnx.commit()

    def write_records(self, records):
        for record in records:
            self.write_record(record, commit=False)
        self._cnx.commit()

    def get_records(self, uuid, start, end, fields=None):
        query = self._cnx.query(Record).filter(Record.uuid == uuid)

        # make input time parameters UTC or force it
        def to_utc(dt):
            if dt.tzinfo is None:
                return dt.replace(tzinfo=pytz.utc)
            else:
                return dt.astimezone(pytz.utc)
        start_dt = to_utc(start)
        end_dt = to_utc(end)
        query = query.filter(Record.ts >= start_dt).filter(Record.ts <= end_dt)

        # filter which fields
        if fields is not None:
            query = query.filter(Record.key.in_(fields))

        for rec in query.all():
            yield Record.to_tuple(rec)


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
