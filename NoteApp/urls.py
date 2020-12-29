from django.urls import path
from .views import AllNotesAPI
urlpatterns = [
    path('', AllNotesAPI.as_view(), name="all"),
    ]
