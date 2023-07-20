import json

from celery.bin.control import inspect
from django.contrib.auth.models import Permission
from django.db.models import Count, FilteredRelation, Q, Prefetch
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiParameter
from rest_framework import viewsets, views, status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated

from notifications import celery_app
from .tasks import send_messages
from django_celery_results.models import TaskResult

from .models import Message, Notification
from .serializers import NotificationSerializer, MessageSerializer, NotificationInfoSerializer


def revoke_task_by_notification_pk(pk: int):
    i = celery_app.control.inspect().scheduled()
    tasks = i['celery@worker']
    for j in tasks:
        if j['request']['args'][0] == pk:
            celery_app.control.revoke(task_id=j['request']['id'], terminate=True, signal='SIGKILL')

class NotificationViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer


    @extend_schema(
        description="Get list of notifications",
        summary="Get notifications list",
        auth=None,
        parameters=[
            OpenApiParameter("id", OpenApiTypes.INT, OpenApiParameter.PATH, description="Id of the notification")
        ],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    @extend_schema(
        description="Retrive notification by id",
        summary="Get notification",
        auth=None,
        parameters=[
            OpenApiParameter("id", OpenApiTypes.INT, OpenApiParameter.PATH, description="Id of the notification")
        ],
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        description="Creations of message sender task",
        summary="create a notification",
        examples=[
            OpenApiExample(
                'Example of notification',
                value={
                    "start_time": "2023-07-20T10:30:13.434Z",
                    "end_time": "2023-07-23T11:30:13.434Z",
                    "message_text": "string",
                    "filter": {
                        "tag": ["string"],
                        "operator_code": [911]
                    }
                }
            )
        ],
        auth=None
    )
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance: Notification = serializer.save()

        start = instance.start_time
        end_time = instance.end_time
        send_messages.apply_async((instance.pk, instance.filter, instance.message_text), eta=instance.start_time,
                                  time_limit=(end_time - start).total_seconds())
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(
        description="Deletes message sending task instance and revokes related celery tasks",
        summary="Delete message sender",
        auth=None
    )
    def destroy(self, request, pk):
        instance = get_object_or_404(Notification, pk=pk)
        revoke_task_by_notification_pk(pk)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        description="Updates message sending task instance and updates (recreates) related celery tasks",
        summary="Updates message sender",
        examples=[
            OpenApiExample(
                'Example of notification',
                value={
                    "start_time": "2023-07-20T10:30:13.434Z",
                    "end_time": "2023-07-23T11:30:13.434Z",
                    "message_text": "string",
                    "filter": {
                        "tag": ["string"],
                        "operator_code": [911]
                    }
                }
            )
        ],
        auth=None
    )
    def update(self, request, pk):
        instance = get_object_or_404(Notification, pk=pk)
        revoke_task_by_notification_pk(pk)
        serializer = self.get_serializer(instance=instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()

        start = instance.start_time
        end_time = instance.end_time
        send_messages.apply_async((instance.pk, instance.filter, instance.message_text), eta=instance.start_time,
                                  time_limit=(end_time - start).total_seconds())

        return Response(serializer.data)

    @extend_schema(
        description="Partial update message sending task instance and updates (recreates) related celery tasks",
        summary="Partial updates message sender",
        examples=[
            OpenApiExample(
                'Example of change 1',
                value={
                    "start_time": "2023-07-20T10:30:13.434Z",
                    "end_time": "2023-07-23T11:30:13.434Z"
                }
            ),
            OpenApiExample(
                'Example of change 2',
                value={
                   'message_text':'new text'
                }
            )
        ],
        auth=None
    )
    def partial_update(self, request, pk):
        instance = get_object_or_404(Notification, pk=pk)
        revoke_task_by_notification_pk(pk)
        serializer = NotificationSerializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()

        start = instance.start_time
        end_time = instance.end_time
        send_messages.apply_async((instance.pk, instance.filter, instance.message_text),
                                  eta=instance.start_time,
                                  time_limit=(end_time - start).total_seconds())

        return Response(serializer.data)


class NotificationListStatistics(views.APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        description="Get short statistics for notifications sending tasks",
        summary="Short statistics",
        auth=None
    )
    def get(self, request):
        notifications = Notification.objects.values('id', 'start_time', 'end_time', 'message_text').annotate(
            created_count=Count('messages', filter=Q(messages__status=Message.StarusChoise.CREATED)),
            processing_count=Count('messages', filter=Q(messages__status=Message.StarusChoise.PROCESSING)),
            complete_count=Count('messages', filter=Q(messages__status=Message.StarusChoise.COMPLETE)),
            error_count=Count('messages', filter=Q(messages__status=Message.StarusChoise.ERROR)),
        )
        return Response(notifications, status=200)


class NotificationStatistics(views.APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        description="Get detailed statistics for notifications sending tasks with messages",
        summary="Detailed statistics",
        auth=None,
        parameters=[
            OpenApiParameter("id", OpenApiTypes.INT, OpenApiParameter.PATH, description="Id of the notification")
        ],
    )
    def get(self, request, pk):
        notifications = Notification.objects.prefetch_related('messages').annotate(
            created_count=Count('messages', filter=Q(messages__status=Message.StarusChoise.CREATED)),
            processing_count=Count('messages', filter=Q(messages__status=Message.StarusChoise.PROCESSING)),
            complete_count=Count('messages', filter=Q(messages__status=Message.StarusChoise.COMPLETE)),
            error_count=Count('messages', filter=Q(messages__status=Message.StarusChoise.ERROR)),
        ).filter(pk=pk)
        # print(notifications[0].__dict__)
        return Response(NotificationInfoSerializer(notifications, many=True).data, status=200)
