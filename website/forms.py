from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from .models import UserProfile, Sample





class SignUpForm(UserCreationForm):
	email = forms.EmailField(widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Email Address'}))
	username = forms.CharField(max_length=25, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Username'}))
	date_of_birth = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'placeholder': 'YYYY-MM-DD',}))
	user_Photo = 'images/profile_picture_default.jpg'

	class Meta:
		model = User
		fields = ('username', 'email', 'date_of_birth', 'password1', 'password2')

	def __init__(self, *args, **kwargs):
		super(SignUpForm, self).__init__(*args, **kwargs)

		self.fields['username'].widget.attrs['class'] = 'form-control'
		self.fields['username'].widget.attrs['placeholder'] = 'Username'
		self.fields['username'].label = ''
		self.fields['username'].help_text = '<span class="form-text text-muted"><small>Required. 25 characters or fewer. Letters, digits and @/./+/-/_ only.</small></span>'

		self.fields['password1'].widget.attrs['class'] = 'form-control'
		self.fields['password1'].widget.attrs['placeholder'] = 'Password'
		self.fields['password1'].label = ''
		self.fields['password1'].help_text = '<ul class="form-text text-muted small"><li>Your password can\'t be too similar to your other personal information.</li><li>Your password must contain at least 8 characters.</li><li>Your password can\'t be a commonly used password.</li><li>Your password can\'t be entirely numeric.</li></ul>'

		self.fields['password2'].widget.attrs['class'] = 'form-control'
		self.fields['password2'].widget.attrs['placeholder'] = 'Confirm Password'
		self.fields['password2'].label = ''
		self.fields['password2'].help_text = '<span class="form-text text-muted"><small>Enter the same password as before, for verification.</small></span>'	

	def save(self, commit=True):
		user = super(SignUpForm, self).save(commit=False)
		user.email = self.cleaned_data['email']
		if commit:
			user.save()
			# Save the UserProfile details
			date_of_birth = self.cleaned_data['date_of_birth']
			# Create the associated UserProfile instance
			UserProfile.objects.create(
				user=user,
				dateOfBirth=date_of_birth,
				userPhoto = self.user_Photo,
				numberOfFollowers=0  # default to 0
			)
		return user

class SampleUploadForm(forms.ModelForm):
    filelocation = forms.FilePathField(allow_files = True, allow_folders = False, path = 'SampleShare/')

    class Meta:
        model = Sample
        fields = ['sampleName', 'fileLocation','isPublic',]
        widgets = {
            'fileLocation': forms.TextInput(attrs={'placeholder': 'Enter file path'}),
			'isPublic': forms.CheckboxInput(),
        }
    def clean_file_location(self):
        file_location = self.cleaned_data.get('fileLocation')

        if not os.path.exists(fileLocation):
            raise forms.ValidationError('File path does not exist.')

        if not os.path.isfile(fileLocation):
            raise forms.ValidationError('The path must point to a file, not a directory.')
        
        valid_extensions = ['.mp3', '.wav']
        file_extension = os.path.splitext(fileLocation)[1]

        if file_extension.lower() not in valid_extensions:
            raise forms.ValidationError(f'Invalid file type. Accepted types: {", ".join(valid_extensions)}')

        if not os.access(file_location, os.R_OK):
            raise forms.ValidationError('The file is not readable.')

        return file_location