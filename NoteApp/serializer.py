from .models import Notes, Label
from rest_framework import serializers
from django.db.models import Q


class LabelAPISerializer(serializers.ModelSerializer):
    class Meta:
        model = Label
        fields = ['label_name']


class RetriveAllNotesSerializer(serializers.ModelSerializer):
    label = LabelAPISerializer(many=True)
    class Meta:
        model = Notes
        fields = ['title', 'content', 'date', 'label','last_updated', 'color']

class LabelSerializer(serializers.Serializer):
    label_name = serializers.CharField(max_length=30, allow_blank=True, allow_null=True)


class AddOrUpdateNotesAPISerializer(serializers.ModelSerializer):
    label = LabelSerializer(many=True, required=False, default=None)
    class Meta:
        model = Notes
        fields = ['title', 'content', 'label', 'color']

    def validate(self, data):
        if not data.get('label'):
            data['label'] = None
        if len(data.get('title')) < 2 or len(data.get('content')) < 2 :
            raise serializers.ValidationError('Too Short Notes Title or Content')
        return data

    def create(self, validated_data):
        label_data = validated_data.pop('label')
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
        return note

class AddNotesForSpecificLabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notes
        fields = ['title','content']

    def validate(self, data):
        if len(data.get('title')) < 2 or len(data.get('content')) < 2 :
            raise serializers.ValidationError('Too Short Notes Title or Content')
        return data