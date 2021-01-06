from .models import Notes, Label
from rest_framework import serializers


class LabelAPISerializer(serializers.ModelSerializer):
    class Meta:
        model = Label
        fields = ['label_name']


class RetriveAllNotesSerializer(serializers.ModelSerializer):
    label = LabelAPISerializer(many=True)
    class Meta:
        model = Notes
        fields = ['title', 'content', 'date', 'label','last_updated']

class LabelSerializer(serializers.Serializer):
    label_name = serializers.CharField(max_length=30)

    def validate(self, data):
        try:
            Label.objects.get(label_name=data.get('label_name'))
        except:
            raise serializers.ValidationError(f"'{data.get('label_name')}' label is not Found")
        return data

class AddOrUpdateNotesAPISerializer(serializers.ModelSerializer):
    label = LabelSerializer(many=True)
    class Meta:
        model = Notes
        fields = ['title', 'content', 'label']

    def validate(self, data):
        if len(data.get('title')) < 2 or len(data.get('content')) < 2 :
            raise serializers.ValidationError('Too Short Notes Title or Content')
        return data
