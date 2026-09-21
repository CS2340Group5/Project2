from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='posts.index'),
    path('postjobs/', views.postjobs, name='posts.postjobs'),
]
