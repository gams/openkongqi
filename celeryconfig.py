import copy
from datetime import timedelta

from openkongqi.source import get_sources


# List of modules to import when celery starts.
CELERY_IMPORTS = ('openkongqi.tasks', )

# Broker settings.
BROKER_URL = 'redis://localhost/0'

# Using the database to store task state and results.
CELERY_RESULT_BACKEND = 'redis://localhost/0'

# celery result serializer
CELERY_RESULT_SERIALIZER = 'json'

# accept only json serialized data
CELERY_ACCEPT_CONTENT = ['json']

# which serializer to use with tasks
CELERY_TASK_SERIALIZER = 'json'

# timezone
CELERY_TIMEZONE = 'Asia/Shanghai'


dyn_schedule = dict()
for source in get_sources():
    dyn_schedule[source['name']] = {
        'task': 'openkongqi.tasks.fetch',
        'schedule': timedelta(minutes=30),
        'args': (source['name'], )
    }

CELERYBEAT_SCHEDULE = copy.copy(dyn_schedule)
