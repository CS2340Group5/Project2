from django.urls import path
from . import views
urlpatterns = [
    path('signup/', views.signup, name='accounts.signup'),
    path('login/', views.login, name='accounts.login'),
    path('logout/', views.logout, name='accounts.logout'),
    path('profile/', views.profile, name='accounts.profile'),
    path('profile/<uuid:id>/', views.profile, name='accounts.profile_view'),
    path('profile/privacy/', views.privacy, name='accounts.privacy'),
    path('profile/edit/', views.edit_profile, name='accounts.edit_profile'),
    path('profile/links/add/', views.add_link, name='accounts.add_link'),
    path('profile/links/<int:id>/delete/', views.delete_link, name='accounts.delete_link'),
]
