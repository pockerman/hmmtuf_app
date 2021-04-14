from django.urls import path

from . import views

urlpatterns = [

    path('hmm_viterbi/',
         views.schedule_hmm_viterbi_compute_view, name='schedule_computation_view'),
    path('hmm_group_viterbi/',
         views.schedule_group_viterbi_compute_view, name='schedule_all_viterbi_compute_view'),

    path('kmers_calculation/',
         views.schedule_kmers_calculation_view, name='schedule_kmers_calculation_view'),
    path('success_schedule_kmer_compute/<str:task_id>/',
         views.success_schedule_kmer_compute_view, name='success_schedule_kmer_compute_view'),
    path('view_kmers/<str:task_id>/',
         views.view_kmers, name='view_kmers'),

    path('view_viterbi_path/<str:task_id>/',
         views.view_viterbi_path, name='view_viterbi_path'),

    path('view_group_viterbi_path/<str:task_id>/',
         views.view_group_viterbi_path, name='view_group_viterbi_path'),

    path('success_schedule_viterbi_computation/<str:task_id>/',
         views.success_schedule_viterbi_compute_view, name='success_schedule_viterbi_computation_view'),

    path('success_schedule_group_viterbi_compute/<str:task_id>/',
         views.success_schedule_group_viterbi_compute_view, name='success_schedule_group_viterbi_compute_view'),

    path('view_group_viterbi_all/<str:task_id>/',
         views.view_group_viterbi_all, name='view_group_viterbi_all'),

    path('success_schedule_group_viterbi_compute_all/<str:task_id>/',
         views.success_schedule_group_viterbi_compute_all_view, name='success_schedule_group_viterbi_compute_all_view'),

    path('repeats_distances_plot/',
         views.view_repeats_distances_plot, name='repeats_distances_plot')

]