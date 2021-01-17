from __future__ import absolute_import, unicode_literals

import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FuntooNote.settings')

app = Celery('FuntooNote')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

app.conf.beat_schedule = {
    'every-day':{
        'task':'NoteApp.tasks.delete_trashed_note',
        'schedule':24*60*60,
    }
}

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')