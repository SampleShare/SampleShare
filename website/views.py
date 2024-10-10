from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404
from .models import Sample, UserProfile
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

from .forms import SignUpForm
from django.contrib.auth.models import User

# Create your views here.
def home(request):

    profiles = UserProfile.objects.all()

    return render(request, 'home.html', {})

def user_detail(request, user_id):
    user_profile = get_object_or_404(UserProfile, id=user_id) #Query UserProfile by ID
    return render(request, 'user_detail.html', {'user_profile': user_profile})

def page_not_found(request):
    raise Http404("Page not here tho")


def profile_page(request, pk):
     if request.user.is_authenticated:
         #Look up profiles
         user_profile = UserProfile.objects.get(id=pk)
         return render(request, 'profile_page.html', {'user_profile':user_profile})
     else:
        messages.success(request, "You must be logged in to view profiles")
        return redirect('home')


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
        
def search_view(request):
    query = request.GET.get('query', '')
    filter_type = request.GET.get('filter', 'username')
    
    if filter_type == 'username':
        results = UserProfile.objects.filter(user__username__icontains=query)
    elif filter_type == 'sample':
        # Logic for filtering by sample will be added once you implement the sample model
        results = []  # Placeholder for now
    
    return render(request, 'your_template.html', {'results': results})      
        