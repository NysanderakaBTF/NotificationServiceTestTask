from django.urls import path
from .views import ClientViewSet

urlpatterns = [
    path('', ClientViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('<int:id>', ClientViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}))
]
