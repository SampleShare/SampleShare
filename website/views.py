from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404, JsonResponse
from .models import UserProfile, Sample
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import SignUpForm, SampleUploadForm
import mutagen
from mutagen.mp3 import MP3
from mutagen.wave import WAVE
import os

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


#Upload Samples
def upload(request):
    if not request.user.is_authenticated:
        messages.error(request, 'You must be logged in to upload a sample.')
        return redirect('login')

    if request.method == 'POST':
        is_public = request.POST.get('is_public') == 'on'  # Global "Public?" checkbox
        files = request.FILES.getlist('file')  # Get uploaded files

        # Get the UserProfile associated with the logged-in user
        try:
            user_profile = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
            messages.error(request, 'No profile found for the current user.')
            return redirect('upload')
            
            sample = Sample(
                userProfile=user_profile,  # Assign logged-in user's profile
                sampleName=uploaded_file.name,
                fileLocation=f'/original/path/{uploaded_file.name}',  # Save the original file location
                isPublic=is_public
            )
            sample.save()

        messages.success(request, 'All valid samples were uploaded successfully.')
        return redirect('upload')

    return render(request, 'upload.html')