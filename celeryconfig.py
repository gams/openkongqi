import copy

from openkongqi.sched import get_schedule

# Constants
SECONDS_PER_MINUTE = 60

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


CELERYBEAT_SCHEDULE = copy.copy(get_schedule(seconds=30 * SECONDS_PER_MINUTE))
