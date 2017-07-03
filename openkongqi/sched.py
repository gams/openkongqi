# -*- coding: utf-8 -*-

from datetime import timedelta

from .source import get_sources


def get_schedule(_sched):
    """Get celery schedule.
    """
    dyn_schedule = dict()
    for source in get_sources():
        dyn_schedule[source['name']] = {
            'task': 'openkongqi.tasks.scrape',
            'schedule': _sched,
            'args': (source['name'], )
        }
    return dyn_schedule
