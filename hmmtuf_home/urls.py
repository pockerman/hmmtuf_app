from django.urls import path

from . import views

urlpatterns = [
    path('', views.home_view, name='index'),
    path('delete_task_directories/', views.delete_task_directories_view, name='delete_task_directories_view'),
]