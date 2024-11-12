from datetime import timedelta
from django.conf import django, settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import (
    Http404,
    HttpRequest,
    StreamingHttpResponse,
    HttpResponse,
    HttpResponseRedirect,
    JsonResponse,
)
from django.http.request import is_same_domain
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.views import View
from django.views.generic import CreateView
from typing import AsyncGenerator
from .forms import (
    SampleEditForm,
    SampleForm,
    SignUpForm,
    PostForm,
    CommentForm,
    MessageForm,
    ProfileForm,
)
from .models import (
    Sample,
    UserProfile,
    Post,
    Comment,
    Chat,
    Message,
    FriendRequest,
    Genre,
)
import asyncio, json, os, mimetypes, logging
from django.http import FileResponse

logger = logging.getLogger(__name__)


# Create your views here.
def home(request):
    profiles = UserProfile.objects.all()
    # Look Up Posts
    userPosts = Post.objects.all()
    return render(request, "home.html", {"userPosts": userPosts})
    # return render(request, "home.html", {})


# --------------------------------------------------------------------#


def user_detail(request, user_id):
    user_profile = get_object_or_404(UserProfile, id=user_id)  # Query UserProfile by ID
    return render(request, "user_detail.html", {"user_profile": user_profile})


# --------------------------------------------------------------------#


def page_not_found(request):
    raise Http404("Page not here tho")


# --------------------------------------------------------------------#


def profile_page(request, username):
    profile_user = get_object_or_404(User, username=username)
    is_owner = request.user == profile_user
    profile = get_object_or_404(
        UserProfile, user=profile_user
    )  # Query UserProfile by ID
    # Check if the logged-in user is a friend
    is_friend = (
        request.user.userprofile.friends.filter(id=profile.id).exists()
        if request.user.is_authenticated
        else False
    )
    # Check if there's a request already sent to viewed profile
    sent_request = (
        request.user.userprofile.sent_requests.filter(to_user=profile).first()
        if request.user.is_authenticated
        else None
    )

    # Check if there's a friend request already sent from the viewed profile.
    received_request = (
        request.user.userprofile.received_requests.filter(from_user=profile).first()
        if request.user.is_authenticated
        else None
    )
    received_requests = FriendRequest.objects.filter(to_user=request.user.userprofile)

    query_all_sample = Sample.objects.filter(userProfiles=profile)

    context = {
        "profile": profile,
        "is_owner": is_owner,
        "is_friend": is_friend,
        "sent_request": sent_request,
        "received_request": received_request,
        "profile_user": profile_user,
        "received_requests": received_requests,
        "query_all_sample": query_all_sample,
    }
    return render(request, "profile_page.html", context)



# --------------------------------------------------------------------#


# Login/Logout/Register Users
def login_user(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        # Authenticate
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "Welcome back")
            return redirect("home")
        else:
            messages.success(request, "Login information incorrect")
            return redirect("login")
    else:
        return render(request, "login.html")


# --------------------------------------------------------------------#


def logout_user(request):
    logout(request)
    messages.success(request, "Logged out")
    return redirect("home")


# --------------------------------------------------------------------#


def register_user(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            # Authenticate & log in
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password1"]
            date_of_birth = form.cleaned_data["date_of_birth"]
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, "Account Registered!")
            return redirect("home")
        else:
            return render(request, "register.html", {"form": form})
    else:
        form = SignUpForm()
        return render(request, "register.html", {"form": form})


@login_required
def send_friend_request(request, user_id):
    to_user_profile = get_object_or_404(UserProfile, user_id=user_id)
    from_user_profile = get_object_or_404(UserProfile, user=request.user)
    # Doesn't create request if there's an existing one.
    if not FriendRequest.objects.filter(
        (
            Q(from_user=from_user_profile, to_user=to_user_profile)
            | Q(from_user=to_user_profile, to_user=from_user_profile)
        )
    ).exists():
        # Prevent sending a friend request to oneself
        if from_user_profile != to_user_profile:
            # Prevents sending if users are already friends
            if not from_user_profile.friends.filter(id=to_user_profile.id).exists():
                FriendRequest.objects.get_or_create(
                    from_user=from_user_profile, to_user=to_user_profile
                )

    return redirect(request.META.get("HTTP_REFERER", "/"))


@login_required
def accept_friend_request(request, request_id):
    friend_request = get_object_or_404(
        FriendRequest, id=request_id, to_user=request.user.userprofile
    )

    # Add each user to the other's friend list
    friend_request.from_user.friends.add(friend_request.to_user)
    friend_request.to_user.friends.add(friend_request.from_user)

    # Delete the friend request
    friend_request.delete()

    return redirect(request.META.get("HTTP_REFERER", "/"))


@login_required
def decline_friend_request(request, request_id):
    # Get the friend request and delete it
    friend_request = get_object_or_404(
        FriendRequest, id=request_id, to_user=request.user.userprofile
    )
    friend_request.delete()  # Simply delete the request

    return redirect(request.META.get("HTTP_REFERER", "/"))


@login_required
def remove_friend(request, user_id):
    friend_profile = get_object_or_404(UserProfile, user_id=user_id)
    user_profile = get_object_or_404(UserProfile, user=request.user)

    # Remove the friendship from both sides
    user_profile.friends.remove(friend_profile)
    friend_profile.friends.remove(user_profile)

    # return redirect('profile', username=friend_profile.user.username)
    return redirect(request.META.get("HTTP_REFERER", "/"))


# ----------------------------Sample Functionality---------------------------------------#


def upload(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            user_profile = UserProfile.objects.get(user=request.user)
            sample_form = SampleForm(request.POST, request.FILES)

            if sample_form.is_valid():
                # Remove commit=False to let the form handle file saving completely
                sample = sample_form.save(commit=False)
                sample.userProfiles = user_profile  # Assign logged-in user
                sample.save()  # This should handle both the file and other field

                genres_data = request.POST.get("genres")
                if genres_data:
                    genres_list = json.loads(genres_data)
                    for genreName in genres_list:
                        genreName = genreName.capitalize()  # Format each genre
                        genre, created = Genre.objects.get_or_create(
                            genreName=genreName
                        )
                        sample.genres.add(genre)  # Associate genre with sample
            else:
                messages.error(request, "Your file is not safe to upload.")

        return render(request, "upload.html")
    else:
        messages.error(request, "You must be logged in to upload a sample file!")
        return redirect("login")


def update_user_samples(request):
    if request.user.is_authenticated:
        user_samples = Sample.objects.filter(
            userProfiles__user=request.user
        ).prefetch_related("genres")
        form = None

        if request.method == "POST":
            sample_id_to_update = request.POST.get("sample_id")
            if sample_id_to_update:
                sample = get_object_or_404(
                    Sample, pk=sample_id_to_update, userProfiles__user=request.user
                )
                # Debugging: Log the incoming isPublic value
                is_public_value = request.POST.get("isPublic") == "True"
                form = SampleEditForm(request.POST, instance=sample)

                # Update the isPublic field based on the checkbox
                sample.isPublic = (
                    is_public_value  # This will be True if the checkbox is checked
                )

                # Debugging: Log the sample's isPublic status before saving
                logging.debug(
                    f"Sample ID: {sample.id}, isPublic before save: {sample.isPublic}"
                )

                # Handle the genres
                if "genres" in request.POST:
                    genre_names = request.POST["genres"].split(",")
                    # Clear existing genres
                    sample.genres.clear()
                    # Add new genres
                    for genre_name in genre_names:
                        genre_name = (
                            genre_name.strip()
                        )  # Remove any leading/trailing whitespace
                        if genre_name:  # Check if it's not an empty string
                            genre, created = Genre.objects.get_or_create(
                                genreName=genre_name
                            )
                            sample.genres.add(genre)

                if form.is_valid():
                    form.save()  # Save the form fields first
                    sample.save()  # Then save the updated privacy status
                    messages.success(
                        request, f"{sample.sampleName} updated successfully!"
                    )
                    return redirect("edit_samples")
        else:
            sample_id_to_update = request.GET.get("update")
            if sample_id_to_update:
                sample = get_object_or_404(
                    Sample, pk=sample_id_to_update, userProfiles__user=request.user
                )
                form = SampleEditForm(instance=sample)

        return render(
            request,
            "edit_samples.html",
            {"user_samples": user_samples, "form": form},
        )
    else:
        messages.error(request, "You need to be logged in to access this page.")
        return redirect("login")


def delete_user_sample(request, sample_id):
    if request.user.is_authenticated:
        try:
            sample_to_delete = get_object_or_404(
                Sample, id=sample_id, userProfiles__user=request.user
            )
            audio_file_path = sample_to_delete.audioFile.path
            sample_to_delete.delete()

            if os.path.exists(audio_file_path):
                os.remove(audio_file_path)
                messages.success(request, "Sample file deleted successfully.")
        except Exception as e:
            messages.warning(request, f"An unexpected error occurred: \n {e}")
    else:
        messages.error(request, "You need to be logged in!")
        return redirect("login")

    return redirect("edit_samples")


def sample_player(request):
    if request.user.is_authenticated:
        query_all_sample = Sample.objects.filter(isPublic=True).select_related(
            "userProfiles"
        )
        return render(
            request, "sample_player.html", {"query_all_sample": query_all_sample}
        )
    else:
        messages.error(request, "You must be logged in to listen to samples.")
        return redirect("login")


# --------------------------------------------------------------------#


def search_user(request):
    if request.method == "GET":
        query = request.GET.get("q")
        filter_type = request.GET.getlist("filter")
        show_all_genres = request.GET.get("show_all_genres", "false") == "true"

        if show_all_genres:
            genres = Genre.objects.all()
            return render(request, "search_results.html", {"all_genres": genres, "show_all_genres": show_all_genres})

        # Default to showing both usernames and samples if no filter is selected
        if not filter_type or "all" in filter_type:
            filter_type = ["username", "sample", "genre"]

        matching_users = User.objects.none()
        matching_samples = Sample.objects.none()
        matching_genres = []

        # Apply the filters based on the selected checkboxes
        if query:
            if "username" in filter_type:
                matching_users = User.objects.filter(username__icontains=query)

            if "sample" in filter_type:
                matching_samples = Sample.objects.filter(
                    sampleName__icontains=query, isPublic=True
                )

            if "genre" in filter_type:
                matching_genres = Genre.objects.filter(
                    genreName__icontains=query
                )
                genre_matching_samples = Sample.objects.filter(
                    genres__in=matching_genres
                ).distinct()

                if genre_matching_samples.exists():
                    matching_samples = matching_samples.union(genre_matching_samples)

        if "all" in filter_type:
            users = matching_users
            samples = matching_samples
            genres = matching_genres
        else:
            users = matching_users if "username" in filter_type else []
            samples = matching_samples if "sample" in filter_type else []
            genres = matching_genres if "genre" in filter_type else []

        return render(
            request,
            "search_results.html",
            {
                "users": matching_users,
                "samples": matching_samples,
                "genres": matching_genres,
                "query": query,
                "filter_type": filter_type,
                "show_all_genres": show_all_genres,
            },
        )

    return render(
        request,
        "search_results.html",
        {
            "users": None,
            "samples": None,
            "genres": None,
            "query": None,
            "filter_type": ["username", "sample", "genre"],
            "show_all_genres": False,
        },
    )


def search_genres(request):
    query = request.GET.get("query", "")
    if query:
        genres = Genre.objects.filter(
            genreName__icontains=query
        )  # Adjust based on your model field
        genre_list = [
            {"name": genre.genreName} for genre in genres
        ]  # Ensure this returns a list of dictionaries
        return JsonResponse(genre_list, safe=False)  # Return the list as JSON
    return JsonResponse([], safe=False)  # Return an empty list if no query


class CreateGenreView(View):
    def post(self, request):
        data = json.loads(request.body)
        genre_names = data.get("genres", [])  # Expecting a list of genre names
        response_data = {"success": True, "created_genres": [], "existing_genres": []}

        # Log the received genre names
        logger.debug("CreateGenreView post method called.")
        logger.debug(f"Request POST data: {data}")

        # Validate that genre_names is a list
        if not isinstance(genre_names, list) or not genre_names:
            response_data["success"] = False
            response_data["message"] = "Genre names must be a non-empty list."
            return JsonResponse(response_data)

        for genre_name in genre_names:
            # Capitalize the first letter & make the rest lowercase
            formatted_genre_name = genre_name.capitalize()

            # Check if the genre already exists
            if not Genre.objects.filter(genreName=formatted_genre_name).exists():
                try:
                    new_genre = Genre.objects.create(genreName=formatted_genre_name)
                    response_data["created_genres"].append(
                        {"genreId": new_genre.id, "genreName": new_genre.genreName}
                    )
                except Exception as e:
                    logger.error(f"Error creating genre '{formatted_genre_name}': {e}")
                    response_data["success"] = False
                    response_data["message"] = (
                        "An error occurred while creating some genres."
                    )
            else:
                response_data["existing_genres"].append(formatted_genre_name)

        return JsonResponse(response_data)


# Used for auto-populating drop-down lists
def search_users(request):
    query = request.GET.get("query", "")
    users = User.objects.filter(username__icontains=query).exclude(
        username=request.user.username
    )  # Adjust filters as needed
    user_data = [
        {"username": user.username, "avatar": user.userprofile.userPhoto.url}
        for user in users
    ]
    return JsonResponse({"users": user_data})


# ----------------------------Post Code -------------------------------#
def posts(request):
    if request.user.is_authenticated:
        # Look Up Posts
        userPosts = Post.objects.all()
        return render(request, "posts.html", {"userPosts": userPosts})
    else:
        messages.success(request, "You Must Be Logged In To Do That...")
        return redirect("home")


def user_post(request, pk):
    if request.user.is_authenticated:
        user_post = Post.objects.get(id=pk)
        comments = Comment.objects.filter(posts=pk)
        post_samples = Post.objects.filter(id=pk)
        #comment_samples = Post.objects.all.prefetch_related("userProfile","samples")
        comment_samples = Comment.objects.filter(~Q(samples=None), posts=pk)
        likes = get_object_or_404(Post, id=pk)
        total_likes = likes.total_likes()

        liked = False
        if likes.likes.filter(id=request.user.id):
            liked = True
        return render(
            request,
            "userPost.html",
            {
                "user_post": user_post,
                "total_likes": total_likes,
                "liked": liked,
                "comments": comments,
                "post_samples":post_samples,
                "comment_samples":comment_samples,
            },
        )
    else:
        messages.success(request, "Your Must Be Logged In...")
        return redirect("home")


def create_post(request, pk):
    if request.user.is_authenticated:
        # current_post = Post.objects.get(id=pk)
        user_samples = Sample.objects.filter(userProfiles=pk)
        user_id = request.user.userprofile
        form = PostForm(request.POST or None, user_id=user_id)
        if request.method == "POST":
            if form.is_valid():
                add_post = form.save()
                messages.success(request, "Post Created...")
                return redirect("home")
        return render(
            request, "create_post.html", {"form": form, "user_samples": user_samples}
        )
    else:
        messages.success(request, "Your Must Be Logged In...")
        return redirect("home")


def update_post(request, pk):
    if request.user.is_authenticated:
        user_id = request.user.userprofile
        current_post = Post.objects.get(id=pk)
        form = PostForm(request.POST or None, user_id=user_id, instance=current_post)
        if request.method == "POST":
            if form.is_valid():
                add_post = form.save()
                messages.success(request, "Post Updated...")
                return redirect("user_post", current_post.id)
        return render(request, "update_post.html", {"form": form, "current_post":current_post})
    else:
        messages.success(request, "Your Must Be Logged In...")
        return redirect("home")


def delete_post(request, pk):
    if request.user.is_authenticated:
        deletePost = Post.objects.get(id=pk)
        deletePost.delete()
        messages.success(request, "Post Was Deleted...")
        return redirect("home")
    else:
        messages.success(request, "You Must Be Logged In To Do That...")
        return redirect("home")


def like_view(request, pk):
    post = get_object_or_404(Post, id=request.POST.get("post_id"))
    # post.likes.add(request.user)
    liked = False
    if post.likes.filter(id=request.user.id).exists():
        post.likes.remove(request.user)
        liked = False
    else:
        post.likes.add(request.user)
        liked = True
    return redirect("user_post", post.id)


# --------------------------------------------------------------------#


def edit_profile(request):
    profile = request.user.userprofile
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()  # Save directly without handling file manually
            return redirect("profile", username=request.user.username)
    else:
        form = ProfileForm(instance=profile)
    return render(request, "edit_profile.html", {"form": form})


# -----------------------Comment Code-----------------------#
class CreateCommentView(CreateView):
    model = Comment
    form_class = CommentForm
    template_name = "create_comment.html"


def create_comment(request, pk):
    if request.user.is_authenticated:
        current_post = Post.objects.get(id=pk)
        userProfile_id = request.user.userprofile
        form = CommentForm(request.POST or None, userProfile_id=userProfile_id)
        if request.method == "POST":
            if form.is_valid():
                add_comment = form.save()
                messages.success(request, "Comment Created...")
                return redirect("user_post", current_post.id)
        return render(
            request, "create_comment.html", {"form": form, "current_post": current_post}
        )
    else:
        messages.success(request, "Your Must Be Logged In...")
        return redirect("home")


def comments(request, pk):
    if request.user.is_authenticated:
        # Look Up Posts
        userComments = Comment.objects.filter(posts=pk)
        user_post = Post.objects.get(id=pk)
        return render(
            request,
            "comments.html",
            {"userComments": userComments, "user_post": user_post},
        )
    else:
        messages.success(request, "You Must Be Logged In To Do That...")
        return redirect("home")


def comment_detail(request, pk):
    if request.user.is_authenticated:
        user_comment = Comment.objects.get(id=pk)
        return render(request, "comment_detail.html", {"user_comment": user_comment})
    else:
        messages.success(request, "Your Must Be Logged In...")
        return redirect("home")


def update_comment(request, pk):
    if request.user.is_authenticated:
        userProfile_id = request.user.userprofile
        current_comment = Comment.objects.get(id=pk)
        current_post = current_comment.posts.id
        form = CommentForm(
            request.POST or None,
            userProfile_id=userProfile_id,
            instance=current_comment,
        )
        if request.method == "POST":
            if form.is_valid():
                add_comment = form.save()
                messages.success(request, "Comment Updated...")
                return redirect("user_post", current_comment.posts.id)
        return render(request, "update_comment.html", {"form": form, "current_post": current_post})
    else:
        messages.success(request, "Your Must Be Logged In...")
        return redirect("home")


def delete_comment(request, pk):
    if request.user.is_authenticated:
        deleteComment = Comment.objects.get(id=pk)
        deleteComment.delete()
        messages.success(request, "Comment Was Deleted...")
        return redirect("user_post", deleteComment.posts.id)
    else:
        messages.success(request, "You Must Be Logged In To Do That...")
        return redirect("home")


# ---------------------------------Delete Account-----------------------------------#
def delete_account(request):
    if request.method == "POST":
        request.user.delete()
        messages.success(request, "Your account has been deleted. ")
        return redirect("home")
    return render(request, "confirm_delete_account.html")


# --------------------------------------------------------------------#


# --------------------Start Chat code---------------------------
@login_required
def delete_chat(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id)

    # Optional: Check if the user is part of the chat before deleting
    if request.user.userprofile in chat.userProfiles.all():
        chat.delete()
        # Redirect to the chat list or another appropriate page
        return redirect("recent_chat_redirect")
    else:
        return redirect(
            "recent_chat_redirect"
        )  # You can add a message for unauthorized deletion if needed


@login_required
def chat(request, chat_id):
    # Get the logged-in user from the session:
    user_profile = get_object_or_404(UserProfile, user=request.user)
    # Retrieves chat room by the room's ID
    chat = get_object_or_404(Chat, id=chat_id)

    # Check if the user is part of the chat's userProfiles (Many-to-Many)
    if user_profile not in chat.userProfiles.all():
        messages.success(request, "You are not part of requested chat.")
        return redirect("recent_chat_redirect")  # Or show an error message

    chatMessages = list(
        chat.message_set.all().order_by("created_at")
    )  # Get messages for the chat

    # Loop through the messages to set show_time and show_name
    for i in range(len(chatMessages)):
        current_message = chatMessages[i]
        current_message.show_time = True
        current_message.day_old = False

        if current_message.created_at < timezone.now() - timezone.timedelta(hours=24):
            current_message.day_old = True  # Set day_old to True if 24 hours or more
        if i == 0:
            current_message.show_name = (
                True  # Automatically show name for the first message
            )
        else:
            previous_message = chatMessages[i - 1]
            # Calculate the time difference between the current and previous message
            time_difference = (
                current_message.created_at - previous_message.created_at
            ).total_seconds()
            # Set show_time to True if time_difference > 600 seconds or if the user has changed
            previous_message.show_time = (
                time_difference > 600 or current_message.user != previous_message.user
            )
            # Set show_name to True if the previous message shows time or if no previous message
            current_message.show_name = previous_message.show_time

    # Fetch all chats that the user is a part of (ordered by timestamp)
    user_chats = Chat.objects.filter(userProfiles=user_profile).order_by(
        "-chatTimeStamp"
    )

    return render(
        request,
        "chat.html",
        {
            "chat": chat,  # Pass the chat room object
            "chats": user_chats,  # Pass the list of chats
            "chatMessages": chatMessages,  # Pass the sorted messages
        },
    )


@login_required
def recent_chat_redirect(request):
    # Get the logged-in user
    user_profile = get_object_or_404(UserProfile, user=request.user)
    # Fetch the most recent chat that the user is part of
    recent_chat = (
        Chat.objects.filter(userProfiles=user_profile)
        .order_by("-chatTimeStamp")
        .first()
    )
    if recent_chat:
        # Redirect to the most recent chat's URL
        return redirect("chat", chat_id=recent_chat.id)
    else:
        # Handle case where no chats exist (redirect to home or show message)
        messages.info(request, "You are not part of any chats.")
        return redirect("home")  # Adjust the redirect as needed


@login_required
def private_chat_redirect(request, user_id):
    # Get the logged-in user
    user_profile = get_object_or_404(UserProfile, user=request.user)
    # Get the profile user (the user whose profile is being visited)
    other_user = get_object_or_404(User, id=user_id)
    other_profile = get_object_or_404(UserProfile, user=other_user)
    users = [other_profile] + [user_profile]

    # Check if the two users are friends
    if other_profile not in user_profile.friends.all():
        return redirect(
            "home"
        )  # Or show an error message (e.g., "You must be friends to chat")
        # Incomplete- Should this send a chat request or just message them directly?

    # Check if a private chat between the two users already exists
    private_chat = (
        Chat.objects.filter(userProfiles=user_profile)
        .filter(userProfiles=other_profile, is_group_chat=False)
        .first()
    )

    if private_chat:
        # Redirect to the existing chat
        return redirect("chat", chat_id=private_chat.id)
    else:
        # If no chat exists, create a new private chat
        new_chat = Chat.objects.create(is_group_chat=False)
        new_chat.userProfiles.set(users)
        new_chat.save()
        if new_chat:
            return redirect("chat", chat_id=new_chat.id)
        else:
            return redirect("home")  # Handle the case where chat creation fails


@login_required
def create_chat(request):
    """
    View to create a new chat. It can handle both private and group chats.
    :param user_ids: List of user IDs to include in the chat
    :param is_group_chat: Boolean flag to determine if it's a group chat
    :param chat_name: Optional name for group chats
    """
    user_profile = get_object_or_404(UserProfile, user=request.user)

    if request.method == "POST":
        chat_name = request.POST.get("chat_name")
        chat_usernames = request.POST.get("chat_users").split(
            ","
        )  # Get the list of usernames from form
        other_users = UserProfile.objects.filter(
            user__username__in=chat_usernames
        )  # Fetch users by username

        if len(other_users) < 1:
            messages.info(request, "Cannot make a chat with only one user.")
            return redirect(recent_chat_redirect)

        # Ensure the current user is included in the chat
        users = list(other_users) + [user_profile]

        # Check for an existing private chat between the current user and the other user
        if (
            len(users) == 2
        ):  # Only check if there are exactly two users (one current user and one other)
            existing_chat = (
                Chat.objects.filter(is_group_chat=False, userProfiles=user_profile)
                .filter(userProfiles__in=other_users)
                .distinct()
                .first()
            )
            if existing_chat:
                other_user = users[0] if users[1] == user_profile else users[1]
                messages.info(
                    request,
                    f"You already have an active chat with {other_user.user.username}.",
                )
                return redirect(
                    "chat", chat_id=existing_chat.id
                )  # Redirect to existing chat

        # Determine if this is a group chat
        is_group_chat = len(users) > 2

        # Create the chat instance
        chat = Chat.objects.create(is_group_chat=is_group_chat)
        if is_group_chat:
            chat.chatName = chat_name  # Set the chat name for group chats

        # Add users to the chat
        chat.userProfiles.set(users)
        chat.save()

        return redirect(
            "chat", chat_id=chat.id
        )  # Redirect after successful chat creation (adjust to your desired route)

    return render(
        request, "create_chat.html"
    )  # Render the form page in case of GET request


@login_required  # Ensure user is logged in
def add_message(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id)  # Retrieve the chat instance
    chatMessages = list(
        chat.message_set.all().order_by("created_at")
    )  # Get messages for the chat

    if request.method == "POST":
        form = MessageForm(request.POST)
        if form.is_valid():
            content = form.cleaned_data["content"]
            # Create the new message instance
            Message.objects.create(chat=chat, user=request.user, content=content)
            chat.chatTimeStamp = timezone.now()
            chat.save()
            return redirect(
                "chat", chat_id=chat_id
            )  # Redirect to the chat page after posting
    else:
        # Form is invalid, render the chat page with errors
        messages.error(
            request, "There was an error with your submission."
        )  # Optional: Flash an error message
        messages = chat.message_set.all().order_by(
            "created_at"
        )  # Fetch messages for the chat
        return render(
            request,
            "chat.html",
            {
                "chat": chat,
                "user_profile": request.user.userprofile,
                "chats": Chat.objects.filter(
                    userProfiles=request.user.userprofile
                ).order_by("-chatTimeStamp"),
                "chatMessages": chatMessages,
                "form": form,  # Pass the form back with errors
            },
        )

    return redirect("chat", chat_id=chat_id)


# ---------------------End chat Code------------------------------


# ------------------------ download code-------------------------#


def download_sample(request, pk):
    current_sample = get_object_or_404(Sample, id=pk)
    file_path = current_sample.audioFile.path
    response = FileResponse(open(file_path, "rb"))
    response["Content-Type"] = "application/octet-stream"
    stringFilePath = str(current_sample.audioFile)
    # if the audio file location ends with a 3 we can assume its an .mp3 file
    # else we will assume its a .wav file
    if stringFilePath.endswith(".mp3"):
        response["Content-Disposition"] = (
            f'attachment; filename="{current_sample.sampleName}.mp3"'
        )
    else:
        response["Content-Disposition"] = (
            f'attachment; filename="{current_sample.sampleName}.wav"'
        )

    return response
