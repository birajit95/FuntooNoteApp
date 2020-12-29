from django.http import HttpResponse
from rest_framework.renderers import JSONRenderer
from rest_framework.generics import GenericAPIView
from .serializer import RetriveAllNotesSerializer, AddNotesAPISerializer
from .models import Notes
from django.db.models import Q
from rest_framework import status

class AllNotesAPI(GenericAPIView):
    serializer_class = RetriveAllNotesSerializer
    def get(self, request):
        allNotes = Notes.objects.filter(Q(is_archive=False) & Q(user=request.user.pk))
        serializer = self.serializer_class(allNotes, many=True)
        return HttpResponse(JSONRenderer().render(serializer.data))

class AddNotesAPI(GenericAPIView):
    serializer_class = AddNotesAPISerializer
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            Notes(user=request.user, title=serializer.data.get('title'),
                  content=serializer.data.get('content')).save()
            responseMsg = {'msg':'Your note is saved', 'status':status.HTTP_201_CREATED}
            return HttpResponse(JSONRenderer().render(responseMsg))
        return HttpResponse(JSONRenderer().render(serializer.errors))
