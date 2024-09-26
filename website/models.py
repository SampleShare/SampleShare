from django.db import models

# Create your models here.

# ------User-Profiles---------------
# username = VARCHAR(50) NOT NULL
# dataOfBirth = VARCHAR(50) NOT NULL
# email = VARCHAR(50) NOT NULL
# password = VARCHAR(50) NOT NULL
# userPhote = VARCHAR (50) NOT NULL
# bio = TEXT NOT NULL
#------------------------------------
class UserProfile(models.Model):
    username = models.CharField(max_length=50, unique=True)
    dateOfBirth = models.CharField(max_length=50)
    email = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=50)
    userPhoto = models.TextField()
    bio = models.TextField()
    numberOfFollowers = models.IntegerField()

    def __str__(self):
        return(f"{self.username} {self.dateOfBirth} {self.email} {self.password} {self.userPhoto} {self.bio} {self.numberOfFollowers}")

# ------Samples------
# samplename = VARCHAR(50) NOT NULL
# fileLocation = VARCHAR(50) NOT NULL
# isPublic = BOOLEAN NOT NULL
#------------------------------------
class Sample(models.Model):
    sampleName = models.CharField(max_length = 50)
    fileLocation = models.TextField()
    isPublic = models.BooleanField()
    # Many to Many with UserProfiles
    userProfiles = models.ManyToManyField(UserProfile, null=True)
    def __str__(self):
        return(f"{self.sampleName} {self.fileLocation} {self.isPublic}")

class Chat(models.Model):
    chatName = models.CharField(max_length = 50)
    chatTimeStamp = models.DateTimeField(auto_now_add=True)
    # Many to Many with UserProfiles
    userProfiles = models.ManyToManyField(UserProfile, null=True)
    def __str__(self):
        return(f"{self.chatName} {self.chatTimeStamp}")

class Message(models.Model):
    message = models.TextField()
    messageTimeStamp = models.DateTimeField(auto_now_add=True)
    # one to many with Chats
    chats = models.ForeignKey(Chat, on_delete=models.CASCADE)
    # one to many with samples
    samples = models.ManyToManyField(Sample)
    def __str__(self):
        return(f"{self.message} {self.messageTimeStamp}")

class Genre(models.Model):
    genreName = models.CharField(max_length = 50)
    # one to many with samples
    samples = models.ManyToManyField(Sample, null=True)
    def __str__(self):
        return(f"{self.genreName}")

class Post(models.Model):
    postText = models.TextField()
    postTimeStamp = models.DateTimeField(auto_now_add=True)
    # one to many with samples
    samples = models.ForeignKey(Sample, on_delete=models.CASCADE, null=True)
    # Many to Many with user-Profiles
    userProfiles = models.ManyToManyField(UserProfile, null=True)

    def __str__(self):
        return(f"{self.postText} {self.postTimeStamp}")

class Comment(models.Model):
    commentMessage = models.TextField()
    commentTimeStamp = models.DateTimeField(auto_now_add=True)
    # One to Many with Posts
    posts = models.ForeignKey(Post, on_delete=models.CASCADE)
    # One to Many with Samples
    samples = models.ForeignKey(Sample, on_delete=models.CASCADE, null=True)
    def __str__(self):
        return(f"{self.commentMessage} {self.commentTimeStamp}")