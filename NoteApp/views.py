from rest_framework.generics import GenericAPIView
from .serializer import RetriveAllNotesSerializer, AddOrUpdateNotesAPISerializer, LabelAPISerializer, AddNotesForSpecificLabelSerializer
from .models import Notes, Label
from django.db.models import Q
from rest_framework import status
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta
from rest_framework.response import Response
import sys
sys.path.append("..")
from FuntooNote.logger import logger
from FuntooNote.redis_cache import Cache
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
import json


@method_decorator(login_required(login_url='/user/login/'), name='dispatch')
class AllNotesAPI(GenericAPIView):
    serializer_class = RetriveAllNotesSerializer
    def get(self, request):
        """
        This API is used to fetch all notes of the user
        @return: returns all notes
        """
        allNotes = Notes.objects.filter(Q(is_archive=False) & Q(user=request.user.pk) & Q(is_trash=False))
        if not allNotes:
            logger.info(f"{request.user.username}'s no notes present")
            return Response({'response_data': 'No notes available'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(allNotes, many=True)
        logger.info(f"{request.user.username}'s all notes accessed")
        return Response({'response_data':serializer.data}, status=status.HTTP_200_OK)


@method_decorator(login_required(login_url='/user/login/'), name='dispatch')
class AddNotesAPI(GenericAPIView):
    serializer_class = AddOrUpdateNotesAPISerializer
    def post(self, request):
        """
        This API is used to create a note for user
        @param request: It takes note title, content, label(optional) and color(optional)
        @return: creates not on successful validation
        """
        serializer = self.serializer_class(data=request.data, context={'user':request.user})
        if serializer.is_valid():
            serializer.save()
            logger.info(f"{request.user.username}'s note is saved")
            return Response({'response_msg':'Your note is saved'}, status=status.HTTP_201_CREATED)
        logger.error(serializer.errors)
        return Response({'response_msg':serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(login_required(login_url='/user/login/'), name='dispatch')
class UpdateNotesAPI(GenericAPIView):
    serializer_class = AddOrUpdateNotesAPISerializer
    def patch(self, request, note_id):
        """
        This API is used to update the existing note
        @param request: title, content, label, color
        @param note_id: primary_key of the specific note
        @return: updates the note
        """
        try:
            note = Notes.objects.get(Q(pk=note_id) & Q(user=request.user))
        except Notes.DoesNotExist:
            logger.warning("Note does not exist on update API hit")
            return Response({'msg': 'Your not authorised to access this data'},status=status.HTTP_401_UNAUTHORIZED)
        serializer = self.serializer_class(data=request.data, partial=True)
        if serializer.is_valid():
            note.last_updated = datetime.now()
            note.title = serializer.data.get('title')
            note.content = serializer.data.get('content')
            note.color = serializer.data.get('color')
            if serializer.data.get('label'):
                for label in serializer.data.get('label'):
                    try:
                        Label.objects.get(Q(label_name=label['label_name']) & Q(user=request.user))
                    except Label.DoesNotExist:
                        logger.warning(f"{label['label_name']} does not exist")
                        return Response({'response_msg': 'This label is not exist'}, status=status.HTTP_404_NOT_FOUND)
                note.label.clear()
            if serializer.data.get('label'):
                for label in serializer.data.get('label'):
                        label_obj = Label.objects.get(Q(label_name=label['label_name']) & Q(user=request.user))
                        note.label.add(label_obj)
            note.save()
            logger.info("Note is updated")
            return Response({'response_msg': 'Your note is Updated'}, status=status.HTTP_200_OK)
        logger.error(serializer.errors)
        return Response({'response_msg':serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(login_required(login_url='/user/login/'), name='dispatch')
class DeleteNotesAPI(GenericAPIView):
    def delete(self, request, note_id):
        """
        This API is used to delete and trash existing note
        @param note_id: primary_key of the specific note
        @return: trash or delete the note if it is already trashed
        """
        try:
            note = Notes.objects.get(Q(pk=note_id) & Q(user=request.user))
            if note.is_trash:
                note.delete()
                logger.info("Note is deleted permanently")
                return Response({'response_msg': 'Your Note is deleted permanently'}, status=status.HTTP_200_OK)
            else:
                note.is_trash = True
                note.save()
                logger.info("Note is Trashed")
                return Response({'response_msg': 'Your Note is trashed'}, status=status.HTTP_200_OK)
        except Notes.DoesNotExist:
            logger.warning("Note does not exist")
            return Response({'response_msg': 'This Note is not exist'}, status=status.HTTP_404_NOT_FOUND)


@method_decorator(login_required(login_url='/user/login/'), name='dispatch')
class AddLabelAPI(GenericAPIView):
    serializer_class = LabelAPISerializer
    def post(self, request):
        """
        This API is used to create a label
        @param request: label name
        @return: Creates label
        """
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            Label(user=request.user, label_name=serializer.data.get('label_name')).save()
            logger.info("label created")
            return Response({'response_msg':'Label added'},status=status.HTTP_201_CREATED)
        logger.error(serializer.errors)
        return Response({'response_msg':serializer.errors},status=status.HTTP_400_BAD_REQUEST)


@method_decorator(login_required(login_url='/user/login/'), name='dispatch')
class RetriveLableAPI(GenericAPIView):
    serializer_class = LabelAPISerializer
    def get(self, request):
        """
        This API is used to get all existing label created by the user
        @param request: Get request
        @return: returns all existing label
        """
        label_data = Label.objects.filter(Q(user=request.user))
        serializer = self.serializer_class(label_data, many=True)
        if not serializer.data:
            logger.info("No label found")
            return Response({'response_data': 'No labels found'}, status=status.HTTP_404_NOT_FOUND)
        logger.info("All labels are accessed")
        return Response({'response_data':serializer.data}, status=status.HTTP_200_OK)

@method_decorator(login_required(login_url='/user/login/'), name='dispatch')
class DeleteLabelAPI(GenericAPIView):
    def delete(self, request, label_name):
        """
        This API is used to delete a specific label
        @param label_name: specific label name to be deleted
        @return: deletes label
        """
        try:
            label = Label.objects.get(Q(label_name=label_name) & Q(user_id=request.user.pk))
            label.delete()
            logger.info(f"{label_name} label is deleted")
            return Response({'response_msg': 'Label deleted'}, status = status.HTTP_200_OK)
        except Label.DoesNotExist:
            logger.info(f"{label_name} label does not exist")
            return Response({'response_msg': f'{label_name} label is not exist'}, status=status.HTTP_404_NOT_FOUND)


@method_decorator(login_required(login_url='/user/login/'), name='dispatch')
class AddAndRetrieveNotesForSpecificLabelAPI(GenericAPIView):
    serializer_class = AddNotesForSpecificLabelSerializer
    def get(self, request, label_name):
        """
        This API is used to get label specific notes
        @param label_name: existing specific label name
        @return: Retrieves note for this specific label
        """
        try:
            label = Label.objects.get(Q(label_name=label_name) & Q(user_id=request.user.pk))
            notes = Notes.objects.filter(Q(label=label) & Q(user=request.user.pk) & Q(is_archive=False))
            if not notes:
                logger.info(f"No notes available for label '{label_name}' ")
                return Response({'response_data': f"No notes available for label '{label_name}' "}, status=status.HTTP_200_OK)
            serializer = RetriveAllNotesSerializer(notes, many=True)
            logger.info(f"all notes of {label_name} are fetched")
            return Response({'response_data':serializer.data}, status=status.HTTP_200_OK)
        except (Label.DoesNotExist, Notes.DoesNotExist):
            logger.info(f'{label_name} label is not exist')
            return Response({'response_msg': f'{label_name} label is not exist'}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request, label_name):
        """
        This API is used to create label specific notes
        @param label_name: existing specific label name
        @return: creates note for this specific label
        """
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            try:
                label = Label.objects.get(Q(label_name=label_name) & Q(user_id=request.user.pk))
                note = Notes(user=request.user, title=serializer.data.get('title'),
                             content=serializer.data.get('content'),color=serializer.data.get('color'))
                note.save()
                note.label.add(label)
                logger.info(f"Note is saved")
                return Response({'response_msg':'Your note is saved'}, status=status.HTTP_201_CREATED)
            except Label.DoesNotExist:
                logger.info(f'{label_name} label is not exist')
                return Response({'response_msg': f'{label_name} label is not exist'}, status=status.HTTP_404_NOT_FOUND)
        logger.error(serializer.errors)
        return Response({'response_msg': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

@method_decorator(login_required(login_url='/user/login/'), name='dispatch')
class TrashNotesAPI(GenericAPIView):
    serializer_class = RetriveAllNotesSerializer
    def get(self, request):
        """
        This API is used to get all trashed notes
        @param request: get request
        @return: Returns all trashed notes
        """
        notes =Notes.objects.filter(Q(user=request.user.pk) & Q(is_trash=True))
        if not notes:
            logger.info(f"Trash is empty")
            return Response({'response_data': 'No notes in Trash'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(notes, many=True)
        logger.info(f"All trashed notes are accessed")
        return Response({'response_data':serializer.data}, status=status.HTTP_200_OK)

@method_decorator(login_required(login_url='/user/login/'), name='dispatch')
class UnTrashNotesAPI(GenericAPIView):
    def patch(self, request, note_id):
        """
        This API is used to restore trashed note
        @param note_id: primary_key of the specific note
        @return: Restores the note
        """
        try:
            note = Notes.objects.get(Q(pk=note_id) & Q(user=request.user.pk) & Q(is_trash=True))
            note.is_trash = False
            note.save()
            logger.info("Note is restored")
            return Response({'response_msg': 'Your Note is restored'}, status=status.HTTP_200_OK)
        except Notes.DoesNotExist:
            logger.info("Note does not exist")
            return Response({'response_msg': 'This Note is not exist'}, status=status.HTTP_404_NOT_FOUND)


@method_decorator(login_required(login_url='/user/login/'), name='dispatch')
class SearchNoteView(GenericAPIView):
    serializer_class = RetriveAllNotesSerializer
    query = openapi.Parameter(
        'query', in_=openapi.IN_QUERY, description='Description',
        type=openapi.TYPE_STRING
    )
    @swagger_auto_schema(manual_parameters=[query])
    def get(self, request):
        """
        This API is used to search notes by serch query
        @param request: search query
        @return: returns the note if match found
        """
        query = request.GET.get('query')
        if not query:
            logger.info('Query string is blank')
            return Response({'response_msg':'Cant Process blank request'}, status=status.HTTP_400_BAD_REQUEST)
        cache = Cache.getCacheInstance()
        datalist = []
        cache_flag = False
        for key in cache.keys('*'):
            if 'Note' in str(key):
                data = json.loads(cache.hmget(name=key.decode('utf-8'), keys='noteObj')[0])
                if query.lower() in data['title'].lower() or query.lower() in data['content'].lower() :
                    cache_flag = True
                    datalist.append(data)
        if cache_flag:
            logger.info('Notes accessed from cache')
            return Response({'form_cache response_msg':datalist}, status=status.HTTP_200_OK)
        notes = Notes.objects.filter(Q(title__icontains=query) | Q(content__icontains=query)
                                     | Q(color__icontains=query) & Q(user=request.user.pk))
        serializer = self.serializer_class(notes,many=True)
        note_ids = []
        for note in notes:
            note_ids.append(note.id)
        note_ids = iter(note_ids)
        for note in serializer.data:
            id_no = next(note_ids)
            cache.hmset(f'Note-{id_no}',{'noteObj':json.dumps(note)})
            cache.expire(f'Note-{id_no}',time=timedelta(days=3))
        if len(serializer.data):
            logger.info('Notes accessed from database')
            return Response({'response_msg':serializer.data}, status=status.HTTP_200_OK)
        logger.info('Search result not found')
        return Response({'response_msg':'Search results not found'}, status=status.HTTP_404_NOT_FOUND)