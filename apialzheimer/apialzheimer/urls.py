"""
URL configuration for apialzheimer project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.urls import include, path, re_path

from app.View import views

from . import urls

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


urlpatterns = [
    path("admin/", admin.site.urls),
    #re_path(r'^nuevasolicitud/$',views.Clasificacion.determinarAprobacion),
    re_path(r'^predecir/',views.Clasificacion.predict_image),
    re_path(r'^login/',views.Clasificacion.procesar_usuario),
    #re_path(r'^predecirIOJson/',views.Clasificacion.predecirIOJson),
    re_path(r'^createuser/', views.Clasificacion.Crear_Usuario),
    #re_path(r'^saveRadiografia/', views.Clasificacion.Crear_Radiografia),
    re_path(r'^make/', views.Clasificacion.MakePrediction),
    re_path(r'^getRadio/', views.Clasificacion.traerRadio),
    re_path(r'^getprofile/', views.Clasificacion.getProfile),
    re_path(r'^editprofile/', views.Clasificacion.editProfile),
    re_path(r'^updatepassword/', views.Clasificacion.editPassword),
    re_path(r'^createPatient/', views.Clasificacion.createPatient),
    re_path(r'^getPatients/', views.Clasificacion.getPatients),
    re_path(r'^modelo/', views.Clasificacion.chatgpt)
]
