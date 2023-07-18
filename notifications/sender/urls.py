from django.urls import path
from .views import NotificationViewSet, MessageViewSet, NotificationListStatistics, NotificationStatistics

urlpatterns = [
    path('notifications/statistics', NotificationListStatistics.as_view()),
    path('notifications/<int:id>/statistics', NotificationStatistics.as_view()),
    path('notifications/<int:id>', NotificationViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'})),
    path('notifications', NotificationViewSet.as_view({'get': 'list', 'post': 'create'})),

    path('messages', MessageViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('messages/<int:id>', MessageViewSet.as_view({'get': 'retrieve',  'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}))
]
