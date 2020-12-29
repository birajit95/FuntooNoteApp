from .models import Notes
from rest_framework import serializers


class RetriveAllNotesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notes
        fields = ['title', 'content', 'date', 'label']


class AddOrUpdateNotesAPISerializer(serializers.ModelSerializer):
    class Meta:
        model = Notes
        fields = ['title', 'content', 'label']
    def validate(self, data):
        if len(data.get('title')) < 2 and len(data.get('content')) < 2 :
            raise serializers.ValidationError('Too Short Notes Title or Content')
        return data

