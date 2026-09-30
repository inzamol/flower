import os
import time
from datetime import datetime

from celery import Celery


from datetime import timedelta
from celery.schedules import crontab

app = Celery("tasks",
             broker=os.environ.get('CELERY_BROKER_URL', 'redis://'),
             backend=os.environ.get('CELERY_RESULT_BACKEND', 'redis'))
app.conf.accept_content = ['pickle', 'json', 'msgpack', 'yaml']
app.conf.worker_send_task_events = True
app.conf.timezone = 'UTC'

app.conf.beat_schedule = {
    'add-every-10-seconds': {
        'task': 'tasks.add',
        'schedule': 10.0,
        'args': (16, 16),
    },
    'echo-every-minute': {
        'task': 'tasks.echo',
        'schedule': timedelta(minutes=1),
        'args': ('Beat ping',),
        'kwargs': {'timestamp': True},
    },
    'quick-ping-every-30s': {
        'task': 'tasks.sleep',
        'schedule': 30.0,
        'args': (1,),
    },
    'cron-sample-every-5-minutes': {
        'task': 'tasks.echo',
        'schedule': crontab(minute='*/5'),
        'args': ('Cron triggered task',),
    },
}


@app.task
def add(x, y):
    return x + y


@app.task
def sleep(seconds):
    time.sleep(seconds)


@app.task
def echo(msg, timestamp=False):
    return "%s: %s" % (datetime.now(), msg) if timestamp else msg


@app.task
def error(msg):
    raise Exception(msg)


if __name__ == "__main__":
    app.start()
