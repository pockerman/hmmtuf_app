from django.urls import path

from . import views

urlpatterns = [
    path('create_hmm/', views.create_hmm_view, name='create_hmm_view'),

]