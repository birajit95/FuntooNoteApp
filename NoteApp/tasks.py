from __future__ import absolute_import, unicode_literals
from celery import shared_task
from .models import Notes
from datetime import datetime, timedelta
from django_celery_results.models import TaskResult
import time

@shared_task()
def delete_trashed_note():
    notes = Notes.objects.filter(is_trash=True)
    for note in notes:
        if datetime.now() - note.trashed_time.replace(tzinfo=None) > timedelta(days=7):
            note.delete()
    time.sleep(1)
    last_10 = TaskResult.objects.all()[:10]
    TaskResult.objects.exclude(task_id__in=list(last_10)).delete()
    return "Trashed deleted"


