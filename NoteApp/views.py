from django.http import HttpResponse
from rest_framework.renderers import JSONRenderer
from rest_framework.generics import GenericAPIView
from .serializer import RetriveAllNotesSerializer, AddOrUpdateNotesAPISerializer, LabelAPISerializer
from .models import Notes, Label
from django.db.models import Q
from rest_framework import status
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required


@method_decorator(login_required(login_url='/user/login/'), name='dispatch')
class AllNotesAPI(GenericAPIView):
    serializer_class = RetriveAllNotesSerializer
    def get(self, request):
        allNotes = Notes.objects.filter(Q(is_archive=False) & Q(user=request.user.pk))
        serializer = self.serializer_class(allNotes, many=True)
        return HttpResponse(JSONRenderer().render(serializer.data))


@method_decorator(login_required(login_url='/user/login/'), name='dispatch')
class AddNotesAPI(GenericAPIView):
    serializer_class = AddOrUpdateNotesAPISerializer
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            Notes(user=request.user, title=serializer.data.get('title'),
                  content=serializer.data.get('content')).save()
            responseMsg = {'msg':'Your note is saved', 'status':status.HTTP_201_CREATED}
            return HttpResponse(JSONRenderer().render(responseMsg))
        return HttpResponse(JSONRenderer().render(serializer.errors))


@method_decorator(login_required(login_url='/user/login/'), name='dispatch')
class UpdateNotesAPI(GenericAPIView):
    serializer_class = AddOrUpdateNotesAPISerializer
    def get(self, request, note_id):
        try:
            note = Notes.objects.get(Q(pk=note_id) & Q(user=request.user))
        except Notes.DoesNotExist:
            responseMsg = {'msg': 'Your not authorised to access this data', 'status': status.HTTP_401_UNAUTHORIZED}
            return HttpResponse(JSONRenderer().render(responseMsg))
        serializer = self.serializer_class(note)
        return HttpResponse(JSONRenderer().render(serializer.data))

    def patch(self, request, note_id):
        try:
            note = Notes.objects.get(Q(pk=note_id) & Q(user=request.user))
        except Notes.DoesNotExist:
            responseMsg = {'msg': 'Your not authorised to access this data', 'status': status.HTTP_401_UNAUTHORIZED}
            return HttpResponse(JSONRenderer().render(responseMsg))
        serializer = self.serializer_class(note, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            responseMsg = {'msg': 'Your note is Updated', 'status': status.HTTP_201_CREATED}
            return HttpResponse(JSONRenderer().render(responseMsg))
        return HttpResponse(JSONRenderer().render(serializer.errors))


@method_decorator(login_required(login_url='/user/login/'), name='dispatch')
class DeleteNotesAPI(GenericAPIView):
    def delete(self, request, note_id):
        try:
            note = Notes.objects.get(Q(pk=note_id) & Q(user=request.user))
            note.delete()
            responseMsg = {'msg': 'Your Note is deleted', 'status': status.HTTP_200_OK}
            return HttpResponse(JSONRenderer().render(responseMsg))
        except Notes.DoesNotExist:
            responseMsg = {'msg': 'Your not authorised to access this data', 'status': status.HTTP_401_UNAUTHORIZED}
            return HttpResponse(JSONRenderer().render(responseMsg))


@method_decorator(login_required(login_url='/user/login/'), name='dispatch')
class AddLabelAPI(GenericAPIView):
    serializer_class = LabelAPISerializer
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            Label(user=request.user, label_name=serializer.data.get('label_name')).save()
            responseMsg = {'msg':'Label added', 'status':status.HTTP_201_CREATED}
            return HttpResponse(JSONRenderer().render(responseMsg))
        return HttpResponse(JSONRenderer().render(serializer.errors))


method_decorator(login_required(login_url='/user/login/'), name='dispatch')
class RetriveLableAPI(GenericAPIView):
    serializer_class = LabelAPISerializer
    def get(self, request):
        label_data = Label.objects.filter(Q(user=request.user))
        serializer = self.serializer_class(label_data, many=True)
        return HttpResponse(JSONRenderer().render(serializer.data))
