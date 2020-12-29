from django.http import HttpResponse
from rest_framework.renderers import JSONRenderer
from rest_framework.generics import GenericAPIView
from .serializer import RetriveAllNotesSerializer
from .models import Notes
from django.db.models import Q

class AllNotesAPI(GenericAPIView):
    serializer_class = RetriveAllNotesSerializer
    def get(self, request):
        allNotes = Notes.objects.filter(Q(is_archive=False) & Q(user=request.user.pk))
        serializer = self.serializer_class(allNotes, many=True)
        return HttpResponse(JSONRenderer().render(serializer.data))
