from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from .models import Sample, UserProfile, Post, Comment


class SampleForm(forms.ModelForm):
    class Meta:
        model = Sample
        fields = ["sampleName", "audioFile", "isPublic", "userProfiles"]
        widgets = {
            "userProfiles": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "value": "",
                    "id": "user",
                    "type": "hidden",
                }
            )
        }


class SampleEditForm(forms.ModelForm):
    class Meta:
        model = Sample
        fields = ["sampleName", "isPublic", "userProfiles"]
        labels = {"isPublic": "Make Sample Public?"}
        widgets = {
            "userProfiles": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "value": "",
                    "id": "user",
                    "type": "hidden",
                }
            )
        }


class SignUpForm(UserCreationForm):
    email = forms.EmailField(
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Email Address"}
        )
    )
    username = forms.CharField(
        max_length=25,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Username"}
        ),
    )
    date_of_birth = forms.DateField(
        widget=forms.DateInput(
            attrs={
                "type": "date",
                "placeholder": "YYYY-MM-DD",
            }
        )
    )
    user_Photo = "images/profile_picture_default.jpg"

    class Meta:
        model = User
        fields = ("username", "email", "date_of_birth", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)

        self.fields["username"].widget.attrs["class"] = "form-control"
        self.fields["username"].widget.attrs["placeholder"] = "Username"
        self.fields["username"].label = ""
        self.fields["username"].help_text = (
            '<span class="form-text text-muted"><small>Required. 25 characters or fewer. Letters, digits and @/./+/-/_ only.</small></span>'
        )

        self.fields["password1"].widget.attrs["class"] = "form-control"
        self.fields["password1"].widget.attrs["placeholder"] = "Password"
        self.fields["password1"].label = ""
        self.fields["password1"].help_text = (
            "<ul class=\"form-text text-muted small\"><li>Your password can't be too similar to your other personal information.</li><li>Your password must contain at least 8 characters.</li><li>Your password can't be a commonly used password.</li><li>Your password can't be entirely numeric.</li></ul>"
        )

        self.fields["password2"].widget.attrs["class"] = "form-control"
        self.fields["password2"].widget.attrs["placeholder"] = "Confirm Password"
        self.fields["password2"].label = ""
        self.fields["password2"].help_text = (
            '<span class="form-text text-muted"><small>Enter the same password as before, for verification.</small></span>'
        )

    def save(self, commit=True):
        user = super(SignUpForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
            # Save the UserProfile details
            date_of_birth = self.cleaned_data["date_of_birth"]
            # Create the associated UserProfile instance
            UserProfile.objects.create(
                user=user,
                dateOfBirth=date_of_birth,
                userPhoto=self.user_Photo,
                numberOfFollowers=0,  # default to 0
            )
        return user


# -----------------Post Form-----------------
class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ("postText", "userProfiles", "samples")

        widgets = {
            "postText": forms.TextInput(attrs={"class": "form-control"}),
            #'userProfiles': forms.Select(attrs={'class': 'form-control'}),
            "userProfiles": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "value": "",
                    "id": "user",
                    "type": "hidden",
                }
            ),
            "sample": forms.Select(attrs={"class": "form-control"}),
        }


# -------------------Profile Form--------------------------------
class ProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ["bio", "userPhoto"]


# ----------------------Comment Code------------------#\


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ("commentMessage", "posts", "samples", "userProfile")

        widgets = {
            "commentMessage": forms.TextInput(attrs={"class": "form-control"}),
            "posts": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "value": "",
                    "id": "post",
                    "type": "hidden",
                }
            ),
            "samples": forms.Select(attrs={"class": "form-control"}),
            "userProfile": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "value": "",
                    "id": "user",
                    "type": "hidden",
                }
            ),
        }


# ----------------------------------------------------#
