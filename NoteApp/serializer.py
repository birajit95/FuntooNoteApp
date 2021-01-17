from .models import Notes, Label
from rest_framework import serializers
from django.db.models import Q
import sys
sys.path.append("..")
from FuntooNote.redis_cache import Cache
from datetime import timedelta
import json
from django.contrib.auth.models import User

class LabelAPISerializer(serializers.ModelSerializer):
    class Meta:
        model = Label
        fields = ['label_name']
    def validate(self, data):
        try:
            Label.objects.get(label_name=data['label_name'], user=self.context.get('user').pk)
            raise serializers.ValidationError("Label is already exist")
        except Label.DoesNotExist:
            return data

class RetriveAllNotesSerializer(serializers.ModelSerializer):
    label = LabelAPISerializer(many=True)
    class Meta:
        model = Notes
        fields = ['title', 'content', 'date', 'label','last_updated', 'color','collaborators']

class LabelSerializer(serializers.Serializer):
    label_name = serializers.CharField(max_length=30, allow_blank=True, allow_null=True)


class AddOrUpdateNotesAPISerializer(serializers.ModelSerializer):
    label = LabelSerializer(many=True, required=False, default=None)
    collaborators = serializers.ListField(required=False, default=None)
    class Meta:
        model = Notes
        fields = ['title', 'content', 'label', 'color','collaborators']

    def validate(self, data):
        if not data.get('label'):
            data['label'] = None
        if len(data.get('title')) < 2 or len(data.get('content')) < 2 :
            raise serializers.ValidationError('Too Short Notes Title or Content')
        if data.get('collaborators'):
            for email in data.get('collaborators'):
                if data['collaborators'].count(email) > 1:
                    raise serializers.ValidationError(f"'{email}' duplicate email found")
                try:
                    user = User.objects.get(email=email)
                    if user.email == self.context['user'].email:
                        raise serializers.ValidationError('email already exists')
                except User.DoesNotExist:
                    raise serializers.ValidationError(f"{email} not found")
        return data

    def create(self, validated_data):
        label_data = validated_data.pop('label')
        collaborators = validated_data.pop('collaborators')
        validated_data['user'] = self.context['user']
        note = Notes.objects.create(**validated_data)
        if label_data:
            for label in label_data:
                if not label['label_name']:
                    break
                try:
                    lb_obj = Label.objects.get(Q(label_name=label['label_name']) & Q(user=note.user))
                    note.label.add(lb_obj)
                except Label.DoesNotExist:
                    note.delete()
                    raise serializers.ValidationError({'response_msg': f"{label['label_name']} label is not exist"})
        collaborators_data = {'owner':note.user.email, 'collaborators':collaborators}
        collaborators = collaborators_data
        note.collaborators=collaborators
        note.save()
        cache = Cache.getCacheInstance()
        cache.hmset(f'user-{note.user.id}-note-{note.id}', {'noteObj': json.dumps(RetriveAllNotesSerializer(note).data)})
        cache.expire(f'user-{note.user.id}-note-{note.id}', time=timedelta(days=3))
        return note

class AddNotesForSpecificLabelSerializer(serializers.ModelSerializer):
    collaborators = serializers.ListField(required=False, default=None)
    class Meta:
        model = Notes
        fields = ['title','content','color','collaborators']

    def validate(self, data):
        if len(data.get('title')) < 2 or len(data.get('content')) < 2 :
            raise serializers.ValidationError('Too Short Notes Title or Content')
        if data.get('collaborators'):
            for email in data.get('collaborators'):
                if data['collaborators'].count(email) > 1:
                    raise serializers.ValidationError(f"'{email}' duplicate email found")
                try:
                    user = User.objects.get(email=email)
                    if user.email == self.context['email']:
                        raise serializers.ValidationError('email already exists')
                except User.DoesNotExist:
                    raise serializers.ValidationError(f"{email} not found")
        return data