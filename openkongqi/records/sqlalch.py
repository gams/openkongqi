# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals
import pytz

from sqlalchemy import create_engine
from sqlalchemy import Column, String, DateTime, Float
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from .base import BaseRecordsWrapper
from ..utils import get_uuid

Base = declarative_base()


class SQLAlchemyRecordsWrapper(BaseRecordsWrapper):

    def __init__(self, settings, cache, *args, **kwargs):
        self._engine = create_engine(self.create_dsn(settings))
        super(SQLAlchemyRecordsWrapper, self).__init__(
            settings, cache, *args, **kwargs
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

    def get_engine(self):
        """Return engine url / data source name (DSN) of database."""
        return self._engine

    def is_duplicate(self, record):
        dup_count = self._cnx.query(Record).filter_by(
            ts=record.ts, uuid=record.uuid, key=record.key
        ).count()
        return dup_count != 0

    def write_records(self, data, context=None):
        for uuid, records in data.items():
            if context.get('modname'):
                rec_uuid = get_uuid(context.get('modname'), uuid)
            else:
                rec_uuid = uuid
            rows = []
            latest = self.get_latest(uuid, context=context)
            if latest is not None:
                # convert from ISO format and convert naive to UTC
                latest_ts = self._string_to_ts(latest['ts'])
                # if latest does exist, limit records to those
                # that are later than the latest timestamp
                records = filter(lambda r: r['ts'] > latest_ts, records)
            last_record = None
            for record in records:
                ts = record['ts'].astimezone(pytz.utc)
                # update last record as we go
                if last_record is None:
                    last_record = record
                else:
                    if ts > last_record['ts']:
                        last_record = record
                # insert the records into SQL database
                for fieldname, value in record['fields'].items():
                    row = Record(ts=ts,
                                 uuid=rec_uuid,
                                 key=fieldname,
                                 value=value)
                    if not self.is_duplicate(row):
                        rows.append(row)
            self._cnx.add_all(rows)
            self._cnx.commit()
            # set latest cache value
            if last_record:
                self.set_latest(uuid, last_record, context=context)

    def get_records(self, uuid, start, end, fields=None):
        query = self._cnx.query(Record) \
            .filter(Record.uuid == self._apply_key_ctx(uuid))

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
