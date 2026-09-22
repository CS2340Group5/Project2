from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='posts.index'),
    path('postjobs/', views.postjobs, name='posts.postjobs'),
    path('viewjobs/', views.viewjobs, name='posts.viewjobs'),
    path('editjob/<int:id>/', views.editjob, name='posts.editjob'),
]
