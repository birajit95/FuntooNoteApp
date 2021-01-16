from __future__ import absolute_import, unicode_literals

import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FuntooNote.settings')

app = Celery('FuntooNote')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

app.conf.beat_schedule = {
    'every-5-seconds':{
        'task':'NoteApp.tasks.send_email',
        'schedule':5,

    }
}

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')