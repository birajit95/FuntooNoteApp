from django.urls import path
from .views import AllNotesAPI, AddNotesAPI, UpdateNotesAPI
urlpatterns = [
    path('', AllNotesAPI.as_view(), name="allNotes"),
    path('add-note/', AddNotesAPI.as_view(), name='addNote'),
    path('update-note/<int:note_id>', UpdateNotesAPI.as_view(), name='updateNote')
    ]
