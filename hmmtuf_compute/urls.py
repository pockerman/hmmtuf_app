from django.urls import path

from . import views

urlpatterns = [

    path('hmm_viterbi/', views.schedule_computation_view, name='schedule_computation_view'),
    path('view_viterbi_path/<str:task_id>/', views.view_viterbi_path, name='view_viterbi_path'),
    path('learn_d3/', views.learn_d3, name='learn_d3'),
]