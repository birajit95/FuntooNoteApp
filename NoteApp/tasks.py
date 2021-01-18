from __future__ import absolute_import, unicode_literals
from celery import shared_task
from .models import Notes
from datetime import datetime, timedelta
from django_celery_results.models import TaskResult
from django.core.mail import EmailMessage

@shared_task()
def delete_trashed_note():
    """This function cleans the trashed note which are older than 7 days"""
    notes = Notes.objects.filter(is_trash=True)
    for note in notes:
        if datetime.now() - note.trashed_time.replace(tzinfo=None) > timedelta(days=7):
            note.delete()
        return "Trashed deleted"


@shared_task()
def clean_task_result_db():
    """This function cleans the task db periodically"""
    last_10 = TaskResult.objects.all()[:50]
    TaskResult.objects.exclude(task_id__in=list(last_10)).delete()


@shared_task()
def sendEmail(user_name, email, note_title):
    """This function sends the email notification to the reminder note owner"""
    current_site = '127.0.0.1:8000'
    relative_url = 'notes/'
    absoluteURL = "http://" + current_site + '/' + relative_url
    email_body = f"Hi {user_name}! You have a note reminder \n {note_title}\n{absoluteURL}"
    data = {'email_body': email_body, 'email_subject': 'Note Reminder', 'to_email': email}
    email = EmailMessage(
        subject=data['email_subject'],
        body=data['email_body'],
        to=(data['to_email'],)
      )
    email.send()

@shared_task()
def send_reminder_notification():
    """This function checks the reminders and sends the notifications"""

    notes = Notes.objects.filter(is_trash=False).exclude(reminder=None)
    for note in notes:
        reminder_timedelta = note.reminder.replace(tzinfo=None) - datetime.now()
        if reminder_timedelta <= timedelta(minutes=1):
            note.reminder = None
            note.save()
            sendEmail.delay(note.user.username, note.user.email, note.title)
            return f'{note} reminder'
