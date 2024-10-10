from django.urls import path
from . import views
from django.http import Http404

urlpatterns = [
    path('', views.home, name='home'),
    path('profile/<str:username>/', views.profile_page, name='profile'),  # Dynamic user page
    path('user/', views.page_not_found),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('register/', views.register_user, name='register'),
    path('search/', views.search_user, name='search_user'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),

]