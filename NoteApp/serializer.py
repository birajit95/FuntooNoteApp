from .models import Notes, Label
from rest_framework import serializers


class RetriveAllNotesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notes
        fields = ['title', 'content', 'date', 'label','last_updated']

class AddOrUpdateNotesAPISerializer(serializers.ModelSerializer):
    class Meta:
        model = Notes
        fields = ['title', 'content', 'label']
    def validate(self, data):
        if len(data.get('title')) < 2 and len(data.get('content')) < 2 :
            raise serializers.ValidationError('Too Short Notes Title or Content')
        return data

class LabelAPISerializer(serializers.ModelSerializer):
    class Meta:
        model = Label
        fields = ['label_name']