from django.urls import path

from . import views

urlpatterns = [

    path('load_bed/', views.load_bed_file_view, name=views.load_bed_file_view.__name__),
    #path('load_region/', views.load_region_view, name='load_region_view'),
    #path('success_load_hmm/<str:hmm_name>/', views.success_load_view_hmm, name='success_load_view_hmm'),
    path('success_load_bed/<str:task_id>/', views.success_load_bed_view, name=views.success_load_bed_view.__name__),
]