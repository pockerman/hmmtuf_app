from django.urls import path

from . import views

urlpatterns = [

    path('hmm_viterbi/', views.schedule_hmm_viterbi_compute_view, name='schedule_computation_view'),
    path('hmm_multi_viterbi/', views.schedule_multi_viterbi_compute_view, name='schedule_hmm_multi_viterbi_view'),
    path('hmm_group_viterbi/', views.schedule_group_viterbi_compute_view, name='schedule_all_viterbi_compute_view'),
    path('view_viterbi_path/<str:task_id>/', views.view_viterbi_path, name='view_viterbi_path'),
    path('view_multi_viterbi_path/<str:task_id>/', views.view_multi_viterbi_path, name='view_multi_viterbi_path'),
    path('success_schedule_multi_viterbi_computation/<str:task_id>/',
         views.success_schedule_multi_viterbi_compute_view, name='success_schedule_multi_viterbi_computation_view'),
    path('success_schedule_viterbi_computation/<str:task_id>/',
         views.success_schedule_viterbi_compute_view, name='success_schedule_viterbi_computation_view'),

]