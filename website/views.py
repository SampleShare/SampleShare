from django.conf import django
from django.http.response import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404
from .models import Sample, UserProfile, Post, Comment
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import SampleForm, SignUpForm, PostForm, CommentForm
from django.contrib.auth.models import User
from django.views.generic import CreateView
from .forms import ProfileForm
from django.conf import settings
import os


# Create your views here.
def home(request):
    profiles = UserProfile.objects.all()
    return render(request, "home.html", {})


def user_detail(request, user_id):
    user_profile = get_object_or_404(UserProfile, id=user_id)  # Query UserProfile by ID
    return render(request, "user_detail.html", {"user_profile": user_profile})


def page_not_found(request):
    raise Http404("Page not here tho")


def profile_page(request, username):
    profile_user = get_object_or_404(User, username=username)

    is_owner = request.user == profile_user

    context = {"profile_user": profile_user, "is_owner": is_owner}

    return render(request, "profile_page.html", context)


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


def logout_user(request):
    logout(request)
    messages.success(request, "Logged out")
    return redirect("home")


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
        form = SignUpForm()
        return render(request, "register.html", {"form": form})
    return render(request, "register.html", {"form": form})


# TODO: need to add a 6 second restriction for audio files.
# and some exception handling for if user is logged or not.
def upload(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            form = SampleForm(request.POST, request.FILES or None)
            if form.is_valid():
                form.save()
                messages.success(request, "Your sample was uploaded successfully!")
                return redirect("home")
        else:
            form = SampleForm()
        return render(request, "upload.html", {"form": form})
    else:
        messages.error(request, "You must be logged in to upload a sample file!")
        return redirect("login")


def search_user(request):
    if request.method == "GET":
        query = request.GET.get("q")
        filter_type = request.GET.get("filter", "all")

        if query:
            if filter_type == "username":
                # Only search for users
                matching_users = User.objects.filter(username__icontains=query)
                matching_samples = []
            elif filter_type == "sample":
                # Only search for samples
                matching_users = []
                matching_samples = Sample.objects.filter(sampleName__icontains=query, isPublic=True)
            else:
                # Search both users and samples
                matching_users = User.objects.filter(username__icontains=query)
                matching_samples = Sample.objects.filter(sampleName__icontains=query, isPublic=True)

            # Check if it's an AJAX request (from fetch) and only return the results part
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return render(request, 'partials/search_results_partial.html', {
                    'users': matching_users,
                    'samples': matching_samples
                })

            # For regular requests, return the full template
            return render(request, 'search_results.html', {
                'users': matching_users,
                'samples': matching_samples,
                'query': query,
                'filter_type': filter_type
            })

        return render(request, 'search_results.html', {'users': None, 'samples': None, 'query': query, 'filter_type': filter_type})



        
def search_view(request):
    query = request.GET.get('query', '')
    filter_type = request.GET.get('filter', 'username')
    
    if filter_type == 'username':
        results = UserProfile.objects.filter(user__username__icontains=query)
    elif filter_type == 'sample':
        # Logic for filtering by sample will be added once you implement the sample model
        results = Sample.objects.filter(sample__sampleName__icontains=query, isPublic=True) 
    
    return render(request, 'your_template.html', {'results': results})      
        
    return render(
                request, "search_results.html", {"users": None, "query": query}
            )


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
        return render(request, "userPost.html", {"user_post": user_post})
    else:
        messages.success(request, "Your Must Be Logged In...")
        return redirect("home")


class CreatePostView(CreateView):
    model = Post
    form_class = PostForm
    template_name = "create_post.html"
    # fields = '__all__'


def update_post(request, pk):

    if request.user.is_authenticated:
        current_post = Post.objects.get(id=pk)
        form = PostForm(request.POST or None, instance=current_post)
        if request.method == "POST":
            if form.is_valid():
                add_post = form.save()
                messages.success(request, "Post Updated...")
                return redirect("home")
        return render(request, "update_post.html", {"form": form})
    else:
        messages.success(request, "Your Must Be Logged In...")
        return redirect("home")


def delete_post(request, pk):
    if request.user.is_authenticated:
        deletePost = Post.objects.get(id=pk)
        deletePost.delete()
        messages.success(request, "Post Was Deleted...")
        return redirect("posts")
    else:
        messages.success(request, "You Must Be Logged In To Do That...")
        return redirect("posts")
# --------------------------------------------------------------------#




def edit_profile(request):
    profile = request.user.userprofile
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()  # Save directly without handling file manually
            return redirect('profile', username=request.user.username)
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'edit_profile.html', {'form': form})

#-----------------------Comment Code-----------------------#

class CreateCommentView(CreateView):
    model = Comment
    form_class = CommentForm
    template_name = "create_comment.html"


def create_comment(request, pk):
    if request.user.is_authenticated:
        current_post = Post.objects.get(id=pk)
        form = CommentForm(request.POST or None)
        if request.method == "POST":
            if form.is_valid():
                add_comment = form.save()
                messages.success(request, "Comment Created...")
                return redirect("posts")
        return render(request, "create_comment.html", {"form": form, "current_post": current_post})
    else:
        messages.success(request, "Your Must Be Logged In...")
        return redirect("home")


def comments(request, pk):
    if request.user.is_authenticated:
        # Look Up Posts
        userComments = Comment.objects.filter(posts=pk)
        user_post = Post.objects.get(id=pk)
        return render(request, "comments.html", {"userComments": userComments,"user_post":user_post})
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
        current_comment = Comment.objects.get(id=pk)
        form = CommentForm(request.POST or None, instance=current_comment)
        if request.method == "POST":
            if form.is_valid():
                add_comment = form.save()
                messages.success(request, "Comment Updated...")
                return redirect("posts")
        return render(request, "update_comment.html", {"form": form})
    else:
        messages.success(request, "Your Must Be Logged In...")
        return redirect("home")

def delete_comment(request, pk):
    if request.user.is_authenticated:
        deleteComment = Comment.objects.get(id=pk)
        deleteComment.delete()
        messages.success(request, "Comment Was Deleted...")
        return redirect("posts")
    else:
        messages.success(request, "You Must Be Logged In To Do That...")
        return redirect("posts")

# --------------------------------------------------------------------#

