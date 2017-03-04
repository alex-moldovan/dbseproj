from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'softeng.settings')

app = Celery('softeng')

# Using a string here means the worker don't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

app.conf.beat_schedule = {
	'restart1am': {
		'task': 'stocks.tasks.stocksfeed',
		'schedule': crontab(hour=1, minute=0, day_of_week="*")
	},
	'yesterdaystats': {
		'task': 'stocks.tasks.updatestats',
		'schedule': crontab(hour=0, minute=30, day_of_week="*")
	},   
}

@app.task(bind=True)
def debug_task(self):
	print('Request: {0!r}'.format(self.request))