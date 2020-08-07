from django.urls import path

from . import views

urlpatterns = [
    # ex: /polls/
    path('load_hmm/', views.load_hmm_json_view, name='load_hmm_json_view'),
    path('load_region/', views.load_region_view, name='load_region_view'),
]