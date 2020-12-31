from django.urls import path
from .views import AllNotesAPI, AddNotesAPI, UpdateNotesAPI, DeleteNotesAPI, AddLabelAPI, RetriveLableAPI, DeleteLabelAPI
urlpatterns = [
    path('', AllNotesAPI.as_view(), name="allNotes"),
    path('add-note/', AddNotesAPI.as_view(), name='addNote'),
    path('update-note/<int:note_id>/', UpdateNotesAPI.as_view(), name='updateNote'),
    path('delete-note/<int:note_id>/', DeleteNotesAPI.as_view(), name='deleteNote'),
    path('add-label/', AddLabelAPI.as_view(), name='addLabel'),
    path('get-labels/', RetriveLableAPI.as_view(), name='getLabels'),
    path('delete-label/<str:label_name>/', DeleteLabelAPI.as_view(), name='deleteLabel'),

]
