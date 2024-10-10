from django.contrib import admin
from .models import UserProfile
from .models import *
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['username',]

# Register your models here.



admin.site.register(Post)
admin.site.register(UserProfile)
admin.site.register(Sample)

