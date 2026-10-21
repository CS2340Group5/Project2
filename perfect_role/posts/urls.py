from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='posts.index'),
    path('recommended/', views.recommended, name='posts.recommended'),
    path('postjobs/', views.postjobs, name='posts.postjobs'),
    path('viewjobs/', views.viewjobs, name='posts.viewjobs'),
    path('editjob/<int:id>/', views.editjob, name='posts.editjob'),
    path('viewbookmarks/', views.viewbookmarks, name='posts.viewbookmarks'),
    path('bookmarktoggle/<int:id>', views.bookmarktoggle, name='posts.bookmarktoggle'),
    path('submitapplication/<int:id>', views.submitapplication, name='posts.submitapplication'),
    path('applications/', views.applications, name='posts.applications'),
    path('pipeline/<int:id>/', views.pipeline, name='posts.pipeline'),
    path('candidates/<int:id>/', views.candidate_recommendations, name='posts.candidate_recommendations'),
    path('application/<int:id>/move/', views.move_application, name='posts.move_application'),
    path('viewpostapplications/<int:id>/', views.viewpostapplications, name = 'posts.view_post_applications'),
    path('requestskill/', views.request_skill, name='posts.request_skill'),
    path('reviewskills/', views.review_skills, name='posts.review_skills'),
    path('deletejob/<int:id>/', views.delete_post, name='posts.delete_post'),
]
