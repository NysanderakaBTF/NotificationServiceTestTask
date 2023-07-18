from django.db.models import Count, FilteredRelation, Q, Prefetch
from rest_framework import viewsets, views, status
from rest_framework.response import Response

from notifications import celery_app
from .tasks import send_messages
from django_celery_results.models import TaskResult

from sender.models import Message, Notification
from sender.serializers import NotificationSerializer, MessageSerializer


class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance: Notification = serializer.save()

        start = instance.start_time
        end_time = instance.end_time
        send_messages.apply_async((instance), eta=instance.start_time, time_limit=(end_time - start).total_seconds())
        return serializer.data

    def destroy(self, request):
        instance = self.get_object()
        results = TaskResult.objects.filter(
            task_args=(instance,)
        ).exclude(
            status='SUCCESS'
        )
        for result in results:
            celery_app.app.control.revoke(task_id=result.task_id)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer


class NotificationListStatistics(views.APIView):

    def get(self, request):
        notifications = Notification.objects.annotate(
            created_count=Count('messages', filter=FilteredRelation('messages', condition=Q(
                messages__status=Message.StarusChoise.CREATED))),
            processing_count=Count('messages', filter=FilteredRelation('messages', condition=Q(
                messages__status=Message.StarusChoise.PROCESSING))),
            complete_count=Count('messages', filter=FilteredRelation('messages', condition=Q(
                messages__status=Message.StarusChoise.COMPLETE))),
            error_count=Count('messages', filter=FilteredRelation('messages', condition=Q(
                messages__status=Message.StarusChoise.ERROR))),
        ).values('id', 'start_time', 'end_time', 'message_text', 'filer', 'created_count', 'processing_count',
                 'complete_count', 'error_count')

        return Response(notifications)


class NotificationStatistics(views.APIView):
    def get(self, request, id):
        notifications = Notification.objects.prefetch_related(
            Prefetch(
                'messages',
                queryset=Message.objects.order_by('status'),
                to_attr='grouped_messages',
            ),
        ).annotate(
            created_count=Count('messages', filter=FilteredRelation('messages', condition=Q(
                messages__status=Message.StarusChoise.CREATED))),
            processing_count=Count('messages', filter=FilteredRelation('messages', condition=Q(
                messages__status=Message.StarusChoise.PROCESSING))),
            complete_count=Count('messages', filter=FilteredRelation('messages', condition=Q(
                messages__status=Message.StarusChoise.COMPLETE))),
            error_count=Count('messages', filter=FilteredRelation('messages', condition=Q(
                messages__status=Message.StarusChoise.ERROR))),
        ).filter(id=id)

        return Response(notifications)
