from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404
from .models import Sample, UserProfile
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

from .forms import SignUpForm
from django.contrib.auth.models import User
from .forms import PostForm
from .models import Post
from django.views.generic import CreateView

# Create your views here.
def home(request):

    profiles = UserProfile.objects.all()

    return render(request, 'home.html', {})

def user_detail(request, user_id):
    user_profile = get_object_or_404(UserProfile, id=user_id) #Query UserProfile by ID
    return render(request, 'user_detail.html', {'user_profile': user_profile})

def page_not_found(request):
    raise Http404("Page not here tho")


def profile_page(request, username):
    profile_user = get_object_or_404(User, username=username)

    is_owner = request.user == profile_user

    context = {
        'profile_user': profile_user,
        'is_owner': is_owner
    }

    return render(request, 'profile_page.html', context)



#Login/Logout/Register Users
def login_user(request):
    if request.method == 'POST':
            username = request.POST['username']
            password = request.POST['password']
            #Authenticate
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, "Welcome back")
                return redirect('home')
            else: 
                messages.success(request, "Login information incorrect")
                return redirect('login')
    else:
        return render(request, 'login.html')

def logout_user(request):
    logout(request)
    messages.success(request, "Logged out")
    return redirect('home')

def register_user(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            #Authenticate & log in
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            date_of_birth = form.cleaned_data['date_of_birth']
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, "Account Registered!")
            return redirect('home')
    else:
        form = SignUpForm()
        return render(request, 'register.html', {'form':form})
    return render(request, 'register.html', {'form':form})

def search_user(request):
    if request.method == "GET":
        query = request.GET.get('q')  # 'q' is the name attribute in your search input field
        if query:
            matching_users = User.objects.filter(username__icontains=query)  # Case-insensitive search
            return render(request, 'search_results.html', {'users': matching_users, 'query': query})
        else:
            return render(request, 'search_results.html', {'users': None, 'query': query})
#----------------------------Post Code -------------------------------#
def posts(request):
    if request.user.is_authenticated:
        # Look Up Posts
        userPosts = Post.objects.all()
        return render(request, 'posts.html', {'userPosts':userPosts})
    else:
        messages.success(request, "You Must Be Logged In To Do That...")
        return redirect('home')

def user_post(request, pk):
    if request.user.is_authenticated:
        user_post = Post.objects.get(id=pk)
        return render(request, 'userPost.html', {'user_post':user_post})
    else:
        messages.success(request, "Your Must Be Logged In...")
        return redirect('home')

#def create_post(request):
    #form = PostForm(request.POST or None)
    #if request.user.is_authenticated:
        #if request.method == "POST":
            #if form.is_valid():
                #add_post = form.save()
                #messages.success(request, "Post Created...")
                #return redirect('home')
        #return render(request, 'create_post.html', {'form':form})
    #else:
        #messages.success(request, "Your Must Be Logged In...")
        #return redirect('home')

class CreatePostView(CreateView):
    model = Post
    form_class = PostForm
    template_name = 'create_post.html'
    #fields = '__all__'


def update_post(request, pk):
    
    if request.user.is_authenticated:
        current_post = Post.objects.get(id=pk)
        form = PostForm(request.POST or None, instance=current_post)
        if request.method == "POST":
            if form.is_valid():
                add_post = form.save()
                messages.success(request, "Post Updated...")
                return redirect('home')
        return render(request, 'update_post.html', {'form':form})
    else:
        messages.success(request, "Your Must Be Logged In...")
        return redirect('home')


def delete_post(request, pk):
    if request.user.is_authenticated:
        deletePost = Post.objects.get(id=pk)
        deletePost.delete()
        messages.success(request, "Post Was Deleted...")
        return redirect('posts')
    else:
        messages.success(request, "You Must Be Logged In To Do That...")
        return redirect('posts')  
#--------------------------------------------------------------------#

        
