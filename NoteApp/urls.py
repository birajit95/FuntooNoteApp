from django.urls import path
from .views import AllNotesAPI, AddNotesAPI
urlpatterns = [
    path('', AllNotesAPI.as_view(), name="allNotes"),
    path('add-note/', AddNotesAPI.as_view(), name='addNote')
    ]
