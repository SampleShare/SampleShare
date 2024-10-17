from .views import CreatePostView, CreateCommentView
from django.urls import path
from . import views
from django.http import Http404
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("", views.home, name="home"),
    path(
        "user/<int:user_id>/", views.user_detail, name="user_detail"
    ),  # Dynamic user page
    path("user/", views.page_not_found),
    path("login/", views.login_user, name="login"),
    path("logout/", views.logout_user, name="logout"),
    path("register/", views.register_user, name="register"),
    path("search/", views.search_user, name="search_user"),
    path("profile/<str:username>/", views.profile_page, name="profile"),
    path("delete-account/", views.delete_account, name="delete_account"),
    # -------Samples/Uploads Links------------#
    path("upload/", views.upload, name="upload"),
    path("sample/", views.sample_player, name="sample_player"),
    # -------Posts Links------------#
    path("posts/", views.posts, name="posts"),
    path("user_post/<int:pk>", views.user_post, name="user_post"),
    # path('create_post/', views.create_post, name ='create_post'),
    path("create_post/", CreatePostView.as_view(), name="create_post"),
    path("update_post/<int:pk>", views.update_post, name="update_post"),
    path("delete_post/<int:pk>", views.delete_post, name="delete_post"),
    path("edit-profile/", views.edit_profile, name="edit_profile"),
    # --------Comment Links--------------#
    path("create_comment/<int:pk>", views.create_comment, name="create_comment"),
    path("comments/<int:pk>", views.comments, name="comments"),
    path("comment_detail/<int:pk>", views.comment_detail, name="comment_detail"),
    path("update_comment/<int:pk>", views.update_comment, name="update_comment"),
    path("delete_comment/<int:pk>", views.delete_comment, name="delete_comment"),
    # --------------------------------------#
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
