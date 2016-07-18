# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals
from copy import copy
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

    def _get_rec_uuid(self, uuid, context=None):
        """Return contextualized station uuid.

        If there exists context with module name, the module name will simply
        be appended in the front for inserting into the database.
        """
        if context is not None:
            moduuid = context.get('moduuid')
            if moduuid:
                return get_uuid(moduuid, uuid)
        return uuid

    def is_duplicate(self, record):
        dup_count = self._cnx.query(Record).filter_by(
            ts=record.ts, uuid=record.uuid, key=record.key
        ).count()
        return dup_count != 0

    def write_records(self, records, ignore_check_latest=False, context=None):
        for uuid, records in records.items():
            rec_uuid = self._get_rec_uuid(uuid, context=context)
            rows = []
            latest = self.get_latest(uuid, context=context)
            # this is a very naive checking of which records to consider
            # when inserting the databse because it simply limits records
            # for those that are later than the latest timestamp
            # however, if we somehow want to manually insert into database
            # records that are before timestamp on `get_latest`
            # none of the records will be inserted
            if not ignore_check_latest and latest is not None:
                records = filter(lambda r: r['ts'] > latest['ts'], records)
            last_record = copy(latest)
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
            if last_record != latest:
                self.set_latest(uuid, last_record, context=context)

    def get_records(self, uuid, start, end, fields=None, context=None):
        # sanitize datetime input
        start_dt = to_utc(start)
        end_dt = to_utc(end)

        rec_uuid = self._get_rec_uuid(uuid, context=context)

        query = self._cnx.query(Record) \
            .filter(Record.uuid == rec_uuid) \
            .filter(Record.ts >= start_dt) \
            .filter(Record.ts <= end_dt)

        # filter which fields
        if fields is not None:
            query = query.filter(Record.key.in_(fields))

        distinct_datetimes = [
            q.ts for q in
            query.group_by('ts')
        ]

        # group by datetime
        for ts in distinct_datetimes:
            yield {
                'ts': ts.replace(tzinfo=pytz.utc),
                'fields': {
                    rec.key: rec.value
                    for rec
                    in query.filter(Record.ts == ts).all()
                },
            }


def to_utc(dt):
    """Make input time parameters UTC or force it."""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=pytz.utc)
    else:
        return dt.astimezone(pytz.utc)


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
