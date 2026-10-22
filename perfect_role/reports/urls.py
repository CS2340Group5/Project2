from django.urls import path
from . import views

urlpatterns = [
    path('post/<int:id>/', views.report_post, name='reports.report_post'),
    path('user/<uuid:id>/', views.report_user, name='reports.report_user'),
    path('review/', views.review_reports, name='reports.review'),
    path('review/<int:id>/', views.report_detail, name='reports.detail'),
]
