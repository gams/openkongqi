# -*- coding: utf-8 -*-

from datetime import timedelta

from .source import get_sources


def get_schedule(seconds):
    """Get celery schedule.
    """
    dyn_schedule = dict()
    for source in get_sources():
        dyn_schedule[source['name']] = {
            'task': 'openkongqi.tasks.fetch',
            'schedule': timedelta(seconds=seconds),
            'args': (source['name'], )
        }
    return dyn_schedule
