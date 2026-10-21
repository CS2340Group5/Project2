from django.urls import path
from . import views

urlpatterns = [
    path('', views.sent_messages, name='messaging.receivedmessages'),
    path('send/<uuid:id>/', views.send_email, name='messaging.send_email'),
]