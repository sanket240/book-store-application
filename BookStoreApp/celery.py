import os
from celery import Celery
from celery.signals import after_setup_task_logger
from celery.app.log import TaskFormatter
# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BookStoreApp.settings')

app = Celery('BookStoreApp')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.conf.beat_schedule = {
    'every-15-seconds': {
        'task': 'books.utils.send_delivery_email',
        'schedule': 15,
        'args': ('sanketdulange@gmail.com',)
    }
}

app.conf.timezone = 'UTC'

app.autodiscover_tasks()


@after_setup_task_logger.connect
def setup_task_logger(logger, *args, **kwargs):
    for handler in logger.handlers:
        handler.setFormatter(
            TaskFormatter('%(asctime)s - %(task_id)s - %(task_name)s - %(name)s - %(levelname)s - %(message)s'))


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
