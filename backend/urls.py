"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.contrib import admin
from django.urls import path, include
from django.urls import re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

...

schema_view = get_schema_view(
   openapi.Info(
      title="Luxeville API",
      default_version='v1',
      description="An API for Hotel Reservations and Management",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="info@devcenter.africa"),
      license=openapi.License(name="Testt License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include("accounts.urls")),
    path('api/v1/rooms/', include("rooms.urls")),
    path('api/v1/reservations/', include("reservations.urls")),
    path('api/v1/', include("common.urls")),
    
    
    ##SWAGGER 
    path('', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

handler404 = 'utils.views.error_404'
handler500 = 'utils.views.error_500'
