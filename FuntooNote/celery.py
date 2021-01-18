from __future__ import absolute_import, unicode_literals

import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FuntooNote.settings')

app = Celery('FuntooNote')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

app.conf.beat_schedule = {
    'every-day':{
        'task':'NoteApp.tasks.delete_trashed_note',
        'schedule':crontab(hour=00,minute=15),
    },
    'every-five-seconds':{
        'task':'NoteApp.tasks.send_reminder_notification',
        'schedule':5
    },
    'clean_taskDB':{
        'task':'NoteApp.tasks.clean_task_result_db',
        'schedule':crontab(hour=00,minute=00)
    }
}

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')