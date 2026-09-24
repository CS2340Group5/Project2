from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='exports.index'),
    path('users/', views.users_csv, name='exports.users'),
    path('jobs/', views.jobs_csv, name='exports.jobs'),
]
