from rest_framework.generics import GenericAPIView
from .serializer import RetriveAllNotesSerializer, AddOrUpdateNotesAPISerializer, LabelAPISerializer, \
    AddNotesForSpecificLabelSerializer, ReminderSerializer
from .models import Notes, Label, ReminderNotes
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
        allNotes = Notes.objects.filter(is_archive=False , is_trash=False)\
            .filter(Q(user=request.user.pk) | Q(collaborators__icontains=request.user.email))
        if not allNotes:
            logger.info(f"{request.user.username}'s no notes present")
            return Response({'response_data': 'No notes available'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(allNotes, many=True, context={'email':request.user.email})
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
            note = Notes.objects.get(Q(pk=note_id) & Q(user=request.user) & Q(is_trash=False))
        except Notes.DoesNotExist:
            logger.warning("Note does not exist on update API hit")
            return Response({'msg': 'Your not authorised to access this data'},status=status.HTTP_401_UNAUTHORIZED)
        serializer = self.serializer_class(data=request.data, partial=True, context={'user':request.user})
        if serializer.is_valid():
            note.last_updated = datetime.now()
            note.title = serializer.data.get('title')
            note.content = serializer.data.get('content')
            note.color = serializer.data.get('color')
            collabortors = serializer.data.get('collaborators')
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
            if note.collaborators:
                note.collaborators.pop('owner')
                note.collaborators.pop('collaborators')
            if collabortors:
                collaborators_json = {'owner':request.user.email,'collaborators':collabortors}
                note.collaborators=collaborators_json
            note.save()
            logger.info("Note is updated")
            cache = Cache.getCacheInstance()
            cache.delete(f'user-{request.user.id}-note-{note.id}')
            cache.hmset(f'user-{request.user.id}-note-{note.id}', {'noteObj': json.dumps(RetriveAllNotesSerializer(note).data)})
            cache.expire(f'user-{request.user.id}-note-{note.id}', time=timedelta(days=3))
            logger.info("Note is updated in cache")
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
            cache = Cache.getCacheInstance()
            cache.delete(f'user-{request.user.id}-note-{note.id}')
            if note.is_trash:
                note.delete()
                logger.info("Note is deleted permanently")
                return Response({'response_msg': 'Your Note is deleted permanently'}, status=status.HTTP_200_OK)
            else:
                note.is_trash = True
                note.trashed_time = datetime.now()
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
        serializer = self.serializer_class(data=request.data, context={'user':request.user})
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
        serializer = self.serializer_class(data=request.data, context={'email':request.user.email})
        if serializer.is_valid():
            try:
                label = Label.objects.get(Q(label_name=label_name) & Q(user_id=request.user.pk))
                note = Notes(user=request.user, title=serializer.data.get('title'),
                             content=serializer.data.get('content'),color=serializer.data.get('color'))
                collaborators = serializer.data.get('collaborators')
                if collaborators:
                    collaborators_json = {'owner':request.user.email, 'collaborators':collaborators}
                    note.collaborators = collaborators_json
                note.save()
                note.label.add(label)
                cache = Cache.getCacheInstance()
                cache.hmset(f'user-{request.user.id}-note-{note.id}',{'noteObj':json.dumps(RetriveAllNotesSerializer(note).data)})
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
        querylist = query.split(' ')
        cache = Cache.getCacheInstance()
        datalist = []
        cache_flag = False
        for key in cache.keys('*'):                                         # checkig if data is available in cache
            if f'user-{request.user.id}-note-' in str(key):
                data = json.loads(cache.hmget(name=key.decode('utf-8'), keys='noteObj')[0])
                for query in querylist:
                    if query.lower() in data['title'].lower() or query.lower() in data['content'].lower():
                        cache_flag = True
                        datalist.append(data)
                    if cache_flag:
                        break
        if cache_flag:
            logger.info('Notes accessed from cache')
            return Response({'response_msg':datalist}, status=status.HTTP_200_OK)
        for query in querylist:
            notes = Notes.objects.filter(Q(title__icontains=query) | Q(content__icontains=query)
                                         | Q(color__icontains=query)).filter(user=request.user.pk, is_trash=False)
            if len(notes):
                break
        serializer = self.serializer_class(notes,many=True)
        note_ids = []
        for note in notes:
            note_ids.append(note.id)
        note_ids = iter(note_ids)
        for note in serializer.data:
            id_no = next(note_ids)
            cache.hmset(f'user-{request.user.id}-note-{id_no}',{'noteObj':json.dumps(note)})
            cache.expire(f'user-{request.user.id}-note-{id_no}',time=timedelta(days=3))
        if len(serializer.data):
            logger.info('Notes accessed from database')
            return Response({'response_msg':serializer.data}, status=status.HTTP_200_OK)
        logger.info('Search result not found')
        return Response({'response_msg':'Search results not found'}, status=status.HTTP_404_NOT_FOUND)

@method_decorator(login_required(login_url='/user/login/'), name='dispatch')
class RemoveSelfEmailByCollaborator(GenericAPIView):
    def delete(self, request, note_id):
        """
        This API is used to delete collaborator's self email from collaborator list
        @param note_id: specific note id
        @return: deletes collaborator's self email from collaborator list
        """
        try:
            note = Notes.objects.get(id=note_id)
            if request.user.email in note.collaborators['collaborators']:
                note.collaborators['collaborators'].remove(request.user.email)
                if not len(note.collaborators['collaborators']):
                    note.collaborators = None
                note.save()
                logger.info('collaborator removes self email')
                return Response({'response_msg':"You have removed yourself from the collaborator"}, status=status.HTTP_200_OK)
            logger.warning('unauthorised access to delete collaborator self email')
            return Response({'response_msg': "Unauthorised access"},status=status.HTTP_401_UNAUTHORIZED)
        except Notes.DoesNotExist:
            logger.info('note is not found')
            return Response({'response_msg':'Note not found'}, status=status.HTTP_404_NOT_FOUND)

@method_decorator(login_required(login_url='/user/login/'), name='dispatch')
class ReminderAddUpdateAPIView(GenericAPIView):
    serializer_class = ReminderSerializer

    def patch(self, request, note_id):
        """
        This API is used to set reminder
        @param note_id: primary_key of specific note
        @return: sets reminder
        """
        try:
            note = Notes.objects.get(id=note_id, user=request.user.id)
        except Notes.DoesNotExist:
            logger.info('Note not found')
            return Response({'response_msg':'Note Not Found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(data=request.data, initial=note, partial=True)
        serializer.is_valid(raise_exception=True)
        note.reminder = serializer.data.get('reminder')
        note.save()
        logger.info('Reminder is set')
        return Response({'response_msg':'Reminder is set'}, status=status.HTTP_200_OK)

    def delete(self, request, note_id):
        """
            This API is used to remove reminder
            @param note_id: primary_key of specific note
            @return: removes reminder
        """
        try:
            note = Notes.objects.get(id=note_id, user=request.user.id)
        except Notes.DoesNotExist:
            logger.info('Note not found')
            return Response({'response_msg':'Note Not Found'}, status=status.HTTP_404_NOT_FOUND)
        note.reminder = None
        note.save()
        logger.info('Reminder is removed')
        return Response({'response_msg':'Reminder is removed'}, status=status.HTTP_200_OK)

class ReminderGetAPIView(GenericAPIView):
    serializer_class = RetriveAllNotesSerializer

    def get(self, request):
        """
            This API is used to fetch all reminder notes of the user
            @return: returns all notes
        """
        Reminder_Notes = ReminderNotes.objects.filter(is_trash=False).\
            filter(Q(user=request.user.pk) | Q(collaborators__icontains=request.user.email)).exclude(reminder=None)
        if not Reminder_Notes:
            logger.info(f"{request.user.username}'s no notes present")
            return Response({'response_data': 'No reminder notes available'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(Reminder_Notes, many=True, context={'email': request.user.email})
        logger.info(f"{request.user.username}'s reminder notes accessed")
        return Response({'response_data': serializer.data}, status=status.HTTP_200_OK)


