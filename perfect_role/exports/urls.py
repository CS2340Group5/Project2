from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='exports.index'),
    path('all/', views.download_all, name='exports.download_all'),
    path('<slug:slug>/', views.download, name='exports.download'),
]