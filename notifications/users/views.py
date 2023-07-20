from django.shortcuts import render
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from .models import Client
from .serializers import ClientSerializer


class ClientViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Client.objects.all()
    serializer_class = ClientSerializer

    @extend_schema(
        description="Get client information by client id",
        summary="Get client",
        auth=None,
        parameters=[
            OpenApiParameter("id", OpenApiTypes.INT, OpenApiParameter.PATH, description="Id of the client")
        ],
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        description="Create client with all information",
        summary="Create client",
        auth=None,
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(
        description="Update client information by client id",
        summary="Update client",
        auth=None,
        parameters=[
            OpenApiParameter("id", OpenApiTypes.INT, OpenApiParameter.PATH, description="Id of the client")
        ],
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(
        description="Delete client by client id",
        summary="Delete client",
        auth=None,
        parameters=[
            OpenApiParameter("id", OpenApiTypes.INT, OpenApiParameter.PATH, description="Id of the client")
        ],
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @extend_schema(
        description="Get list of all clients",
        summary="List of clients",
        auth=None
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        description="Prtial update client information by client id",
        summary="Update client (partial)",
        auth=None,
        parameters=[
            OpenApiParameter("id", OpenApiTypes.INT, OpenApiParameter.PATH, description="Id of the client")
        ],
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)