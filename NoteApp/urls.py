from django.urls import path
from .views import AllNotesAPI, NotesAPI
urlpatterns = [
    path('', AllNotesAPI.as_view(), name="allNotes"),
    path('add-note/', NotesAPI.as_view(), name='addNote')
    ]
