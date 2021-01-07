from django.http import HttpResponse
from rest_framework.renderers import JSONRenderer
from rest_framework.generics import GenericAPIView
from .serializer import RetriveAllNotesSerializer, AddOrUpdateNotesAPISerializer, LabelAPISerializer
from .models import Notes, Label
from django.db.models import Q
from rest_framework import status
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from datetime import datetime
from rest_framework.response import Response

@method_decorator(login_required(login_url='/user/login/'), name='dispatch')
class AllNotesAPI(GenericAPIView):
    serializer_class = RetriveAllNotesSerializer
    def get(self, request):
        allNotes = Notes.objects.filter(Q(is_archive=False) & Q(user=request.user.pk) & Q(is_trash=False))
        serializer = self.serializer_class(allNotes, many=True)
        return Response({'response_data':serializer.data}, status=status.HTTP_200_OK)


@method_decorator(login_required(login_url='/user/login/'), name='dispatch')
class AddNotesAPI(GenericAPIView):
    serializer_class = AddOrUpdateNotesAPISerializer
    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'user':request.user})
        if serializer.is_valid():
            serializer.save()
            return Response({'response_msg':'Your note is saved'}, status=status.HTTP_201_CREATED)
        return Response({'response_msg':serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(login_required(login_url='/user/login/'), name='dispatch')
class UpdateNotesAPI(GenericAPIView):
    serializer_class = AddOrUpdateNotesAPISerializer
    def patch(self, request, note_id):
        try:
            note = Notes.objects.get(Q(pk=note_id) & Q(user=request.user))
        except Notes.DoesNotExist:
            return Response({'msg': 'Your not authorised to access this data'},status=status.HTTP_401_UNAUTHORIZED)
        serializer = self.serializer_class(data=request.data, partial=True)
        if serializer.is_valid():
            note.last_updated = datetime.now()
            note.title = serializer.data.get('title')
            note.content = serializer.data.get('content')
            for label in serializer.data.get('label'):
                try:
                    Label.objects.get(Q(label_name=label['label_name']) & Q(user=request.user))
                except Label.DoesNotExist:
                    return Response({'response_msg': 'This label is not exist'}, status=status.HTTP_404_NOT_FOUND)
            note.label.clear()
            for label in serializer.data.get('label'):
                    label_obj = Label.objects.get(Q(label_name=label['label_name']) & Q(user=request.user))
                    note.label.add(label_obj)
            note.save()
            return Response({'response_msg': 'Your note is Updated'}, status=status.HTTP_200_OK)
        return Response({'response_msg':serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(login_required(login_url='/user/login/'), name='dispatch')
class DeleteNotesAPI(GenericAPIView):
    def delete(self, request, note_id):
        try:
            note = Notes.objects.get(Q(pk=note_id) & Q(user=request.user))
            if note.is_trash:
                note.delete()
                responseMsg = {'msg': 'Your Note is deleted permanently', 'status': status.HTTP_200_OK}
            else:
                note.is_trash = True
                note.save()
                responseMsg = {'msg': 'Your Note is trashed', 'status': status.HTTP_200_OK}
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
        return Response({'response_data':serializer.data}, status=status.HTTP_200_OK)

method_decorator(login_required(login_url='/user/login/'), name='dispatch')
class DeleteLabelAPI(GenericAPIView):
    def delete(self, request, label_name):
        try:
            label = Label.objects.get(Q(label_name=label_name) & Q(user_id=request.user.pk))
            label.delete()
            responseMsg = {'msg': 'Label deleted', 'status': status.HTTP_200_OK}
            return HttpResponse(JSONRenderer().render(responseMsg))
        except Label.DoesNotExist:
            responseMsg = {'msg': 'Your not authorised to access this data', 'status': status.HTTP_401_UNAUTHORIZED}
            return HttpResponse(JSONRenderer().render(responseMsg))


@method_decorator(login_required(login_url='/user/login/'), name='dispatch')
class AddAndRetrieveNotesForSpecificLabelAPI(GenericAPIView):
    serializer_class = AddOrUpdateNotesAPISerializer
    def get(self, request, label_name):
        try:
            label = Label.objects.get(Q(label_name=label_name) & Q(user_id=request.user.pk))
            notes = Notes.objects.filter(Q(label=label) & Q(user=request.user.pk) & Q(is_archive=False))
            serializer = RetriveAllNotesSerializer(notes, many=True)
            return HttpResponse(JSONRenderer().render(serializer.data))
        except (Label.DoesNotExist, Notes.DoesNotExist):
            responseMsg = {'msg': 'Your not authorised to access this data', 'status': status.HTTP_401_UNAUTHORIZED}
            return HttpResponse(JSONRenderer().render(responseMsg))

    def post(self, request, label_name):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            try:
                label = Label.objects.get(Q(label_name=label_name) & Q(user_id=request.user.pk))
                Notes(user=request.user, title=serializer.data.get('title'),
                  content=serializer.data.get('content'), label=label).save()
                responseMsg = {'msg':'Your note is saved', 'status':status.HTTP_201_CREATED}
                return HttpResponse(JSONRenderer().render(responseMsg))
            except Label.DoesNotExist:
                responseMsg = {'msg': 'Your not authorised to access this data', 'status': status.HTTP_401_UNAUTHORIZED}
                return HttpResponse(JSONRenderer().render(responseMsg))
        return HttpResponse(JSONRenderer().render(serializer.errors))

@method_decorator(login_required(login_url='/user/login/'), name='dispatch')
class TrashNotesAPI(GenericAPIView):
    serializer_class = RetriveAllNotesSerializer
    def get(self, request):
        notes =Notes.objects.filter(Q(user=request.user.pk) & Q(is_trash=True))
        serializer = self.serializer_class(notes, many=True)
        return HttpResponse(JSONRenderer().render(serializer.data))

@method_decorator(login_required(login_url='/user/login/'), name='dispatch')
class UnTrashNotesAPI(GenericAPIView):
    def patch(self, request, note_id):
        try:
            note = Notes.objects.get(Q(pk=note_id) & Q(user=request.user.pk) & Q(is_trash=True))
            note.is_trash = False
            note.save()
            responseMsg = {'msg': 'Your Note is restored', 'status': status.HTTP_200_OK}
        except Notes.DoesNotExist:
            responseMsg = {'msg': 'Your not authorised to access this data', 'status': status.HTTP_401_UNAUTHORIZED}
        return HttpResponse(JSONRenderer().render(responseMsg))

