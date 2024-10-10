from django.urls import path
from . import views
from django.http import Http404
from .views import CreatePostView

urlpatterns = [
    path('', views.home, name='home'),
    path('profile/<str:username>/', views.profile_page, name='profile'),  # Dynamic user page
    path('user/', views.page_not_found),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('register/', views.register_user, name='register'),
    path('search/', views.search_user, name='search_user'),
    #-------Posts Links------------#
    path('posts/', views.posts, name ='posts'),
    path('user_post/<int:pk>' , views.user_post, name = 'user_post'),
    #path('create_post/', views.create_post, name ='create_post'),
    path('create_post/', CreatePostView.as_view(), name = 'create_post'),
    path('update_post/<int:pk>', views.update_post, name ='update_post'),
    path('delete_post/<int:pk>', views.delete_post, name = 'delete_post'),
]