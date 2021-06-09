from django.urls import path

from . import views

urlpatterns = [

    path('load_bed/', views.load_bed_file_view, name='load_bed_file_view'),
    #path('load_region/', views.load_region_view, name='load_region_view'),
    #path('success_load_hmm/<str:hmm_name>/', views.success_load_view_hmm, name='success_load_view_hmm'),
    #path('success_load_region/<str:region_name>/', views.success_load_view_region, name='success_load_view_region'),
]