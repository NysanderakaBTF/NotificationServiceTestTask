"""
URL configuration for notifications project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import dj_rest_auth.jwt_auth
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.extensions import OpenApiAuthenticationExtension
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [

    path('auth/', include('dj_rest_auth.urls')),
    path('auth/registration/', include('dj_rest_auth.registration.urls')),

    path('admin/', admin.site.urls),
    path('client/', include('users.urls')),
    path('sender/', include('sender.urls')),
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    # Optional UI:
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]


def custom_preprocessing_hook(endpoints):
    a = []
    for (path, path_regex, method, callback) in endpoints:
        # print(path)
        if not path.startswith('/auth'):
            a.append((path, path_regex, method, callback))
        elif path in ['/auth/login/', '/auth/logout/', '/auth/registration/']:
            a.append((path, path_regex, method, callback))
    return a