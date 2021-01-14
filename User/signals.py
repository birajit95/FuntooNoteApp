from django.db.models.signals import post_delete
from django.contrib.auth.models import User
import sys
sys.path.append('..')
from NoteApp.models import Notes
from NoteApp.serializer import RetriveAllNotesSerializer
from django.dispatch import  receiver
import json
from FuntooNote.redis_cache import Cache
from datetime import timedelta

@receiver(post_delete, sender=User)
def delete_user_signal(sender, instance, using, **kwargs):
    notes = Notes.objects.filter(collaborators__icontains=instance.email)
    serializer = RetriveAllNotesSerializer(notes,many=True)
    cache = Cache.getCacheInstance()
    for note_index,note in enumerate(serializer.data):
        for index,email in enumerate(json.loads(json.dumps(note))["collaborators"].get('collaborators')):
            if email == instance.email:
                notes[note_index].collaborators['collaborators'].pop(index)
                notes[note_index].save()
                cache.hmset(f"user-{notes[note_index].user.id}-note-{notes[note_index].id}",{"noteObj":json.dumps(note)})
                cache.expire(f"user-{notes[note_index].user.id}-note-{notes[note_index].id}",time=timedelta(days=3))



