import json

from celery.bin.control import inspect
from django.contrib.auth.models import Permission
from django.db.models import Count, FilteredRelation, Q, Prefetch
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets, views, status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from notifications import celery_app
from .tasks import send_messages
from django_celery_results.models import TaskResult

from .models import Message, Notification
from .serializers import NotificationSerializer, MessageSerializer, NotificationInfoSerializer


class NotificationViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer

    @extend_schema(

    )

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance: Notification = serializer.save()

        start = instance.start_time
        end_time = instance.end_time
        send_messages.apply_async((instance.pk, instance.filter, instance.message_text), eta=instance.start_time, time_limit=(end_time - start).total_seconds())
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, pk):
        instance = get_object_or_404(Notification, pk=pk)
        # instance = Notification.objects.get(pk=pk)
        i = celery_app.control.inspect().scheduled()
        # print(json.dumps(i, indent=4))
        tasks = i['celery@worker']

        for j in tasks:
            if j['request']['args'][0] == pk:
                celery_app.control.revoke(task_id=j['request']['id'])

        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class MessageViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    queryset = Message.objects.all()
    serializer_class = MessageSerializer


class NotificationListStatistics(views.APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        notifications = Notification.objects.values('id', 'start_time', 'end_time', 'message_text').annotate(
            created_count=Count('messages', filter=Q(messages__status=Message.StarusChoise.CREATED)),
            processing_count=Count('messages', filter=Q(messages__status=Message.StarusChoise.PROCESSING)),
            complete_count=Count('messages', filter=Q(messages__status=Message.StarusChoise.COMPLETE)),
            error_count=Count('messages', filter=Q(messages__status=Message.StarusChoise.ERROR)),
        )
        return Response(notifications, status=200)


class NotificationStatistics(views.APIView):
    permission_classes = [AllowAny]
    def get(self, request, pk):
        notifications = Notification.objects.prefetch_related('messages').annotate(
            created_count=Count('messages', filter=Q(messages__status=Message.StarusChoise.CREATED)),
            processing_count=Count('messages', filter=Q(messages__status=Message.StarusChoise.PROCESSING)),
            complete_count=Count('messages', filter=Q(messages__status=Message.StarusChoise.COMPLETE)),
            error_count=Count('messages', filter=Q(messages__status=Message.StarusChoise.ERROR)),
        ).filter(pk=pk)
        print(notifications[0].__dict__)
        return Response(NotificationInfoSerializer(notifications, many=True).data, status=200)
