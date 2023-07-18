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
        if value.keys() != ["tag", "operator_code"]:
            raise serializers.ValidationError("Filter must contain 'tag' and 'operator_code'")
        if not isinstance(value['tag'], str):
            raise serializers.ValidationError("Filter tag must be a string")
        if not isinstance(value['operator_code'], int):
            raise serializers.ValidationError("Filter operator_code must be a integer")
        return value

    def validate(self, data):
        if data['start_time'] > data['end_time']:
            raise serializers.ValidationError("end must occur after start")
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

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = '__all__'
