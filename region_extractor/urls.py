from django.urls import path

from . import views

urlpatterns = [
    path('extract/', views.extract_region_view, name='extract_region_view'),
]