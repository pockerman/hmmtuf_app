from django.urls import path

from . import views

urlpatterns = [
    path('', views.home_view, name='index'),
    path('sequence_view/', views.sequence_view_request_view, name='sequence_view_request_view'),
    path('sequence_view/<str:ref_seq>/<str:wga_seq>/<str:no_wga_seq>/', views.sequence_view, name='sequence_view'),
]