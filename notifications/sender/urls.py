from django.urls import path
from .views import NotificationViewSet, NotificationListStatistics, NotificationStatistics

urlpatterns = [
    path('notifications/statistics', NotificationListStatistics.as_view()),
    path('notifications/<int:pk>/statistics', NotificationStatistics.as_view()),
    path('notifications/<int:pk>', NotificationViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'})),
    path('notifications', NotificationViewSet.as_view({'get': 'list', 'post': 'create'})),
]
