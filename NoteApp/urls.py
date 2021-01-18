from django.urls import path
from .views import AllNotesAPI, AddNotesAPI, UpdateNotesAPI, DeleteNotesAPI, AddLabelAPI, RetriveLableAPI,\
    DeleteLabelAPI, AddAndRetrieveNotesForSpecificLabelAPI, TrashNotesAPI, UnTrashNotesAPI, SearchNoteView, \
    RemoveSelfEmailByCollaborator, ReminderGetAPIView, ReminderAddUpdateAPIView
urlpatterns = [
    path('', AllNotesAPI.as_view(), name="allNotes"),
    path('add-note/', AddNotesAPI.as_view(), name='addNote'),
    path('update-note/<int:note_id>/', UpdateNotesAPI.as_view(), name='updateNote'),
    path('delete-note/<int:note_id>/', DeleteNotesAPI.as_view(), name='deleteNote'),
    path('add-label/', AddLabelAPI.as_view(), name='addLabel'),
    path('get-labels/', RetriveLableAPI.as_view(), name='getLabels'),
    path('delete-label/<str:label_name>/', DeleteLabelAPI.as_view(), name='deleteLabel'),
    path('notes-for-label/<str:label_name>/', AddAndRetrieveNotesForSpecificLabelAPI.as_view(), name='addNoteForLabel'),
    path('trash/', TrashNotesAPI.as_view(), name='trashNotes'),
    path('un-trash/<int:note_id>/', UnTrashNotesAPI.as_view(), name='unTrashNotes'),
    path('search-note/', SearchNoteView.as_view(), name='searchNote'),
    path('delete-self/<int:note_id>', RemoveSelfEmailByCollaborator.as_view(), name='deleteSelf'),
    path('note-reminder/<int:note_id>', ReminderAddUpdateAPIView.as_view(), name='noteReminder'),
    path('note-reminder/', ReminderGetAPIView.as_view(), name='getReminderNotes'),

]
