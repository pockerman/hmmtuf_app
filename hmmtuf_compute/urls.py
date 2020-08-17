from django.urls import path

from . import views

urlpatterns = [
    # ex: /polls/
    path('hmm_viterbi/', views.schedule_computation_view, name='schedule_computation_view'),
    path('view_viterbi_path/<str:task_id>/', views.view_viterbi_path, name='view_viterbi_path'),
]