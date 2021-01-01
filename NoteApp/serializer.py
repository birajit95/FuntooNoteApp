from .models import Notes, Label
from rest_framework import serializers


class RetriveAllNotesSerializer(serializers.ModelSerializer):
    label = serializers.CharField(max_length=30)
    class Meta:
        model = Notes
        fields = ['title', 'content', 'date', 'label','last_updated']

    def validate(self, data):
        try:
            data['label'] = Label.objects.get(label_name=data.get('label'))
        except Label.DoesNotExist:
            data['label'] = None
        return data


class AddOrUpdateNotesAPISerializer(serializers.ModelSerializer):
    label = serializers.CharField(max_length=30)
    class Meta:
        model = Notes
        fields = ['title', 'content', 'label']

    def validate(self, data):
        try:
            label = Label.objects.get(label_name=data.get('label'))
            data['label'] = label
        except Label.DoesNotExist:
            data['label'] = None
        if len(data.get('title')) < 2 or len(data.get('content')) < 2 :
            raise serializers.ValidationError('Too Short Notes Title or Content')
        return data

class LabelAPISerializer(serializers.ModelSerializer):
    class Meta:
        model = Label
        fields = ['label_name']