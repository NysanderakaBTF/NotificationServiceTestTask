from rest_framework import serializers
from .models import Notification, Message


class NotificationSerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', read_only=True, required=False)
    start_time = serializers.DateTimeField()
    end_time = serializers.DateTimeField()
    message_text = serializers.CharField(max_length=255)
    filter = serializers.JSONField()

    def validate_filter(self, value):
        if not isinstance(value, dict):
            raise serializers.ValidationError("Filter must be a dictionary")
        if list(value.keys()) != ["tag", "operator_code"]:
            raise serializers.ValidationError("Filter must contain 'tag' and 'operator_code'")
        if not isinstance(value['tag'], list) and not value['tag'] is None:
            raise serializers.ValidationError("Filter tag must be a list of strings or None")
        if not value['tag'] is None and not len(value['tag']) > 0 and not isinstance(value['tag'][0], str):
            raise serializers.ValidationError("Filter tag list must contain elements, and elements must be strings")

        if not isinstance(value['operator_code'], list) and not value['operator_code'] is None:
            raise serializers.ValidationError("Filter operator_code must be a list of integers or None")
        if not value['operator_code'] is None and len(value['operator_code']) > 0 and not isinstance(
                value['operator_code'][0], int):
            raise serializers.ValidationError(
                "Filter operator_code list must contain elements, and elements must be integers")

        return value

    def validate(self, data):
        if 'start_time' in data.keys() and 'end_time' in data.keys():
            if data['start_time'] > data['end_time']:
                raise serializers.ValidationError("end must occur after start")
            return data
        return data

    def create(self, validated_data):
        instance = Notification.objects.create(**validated_data)
        return instance

    def update(self, instance: Notification, validated_data):
        for key, value in validated_data.items():
            if key == 'id':
                continue
            setattr(instance, key, value)
        instance.save()
        return instance


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = '__all__'


class NotificationInfoSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True)
    created_count = serializers.IntegerField()
    processing_count = serializers.IntegerField()
    complete_count = serializers.IntegerField()
    error_count = serializers.IntegerField()

    class Meta:
        model = Notification
        fields = ['id', 'start_time','end_time','message_text', 'created_count', 'processing_count', 'complete_count', 'error_count', 'messages']
