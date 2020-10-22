from django.urls import path

from . import views

urlpatterns = [
    path('extract_region/', views.extract_region_view, name='extract_region_view'),
    path('success_extract_region/<str:task_id>/', views.extract_region_success_view, name='extract_region_success_view'),
]