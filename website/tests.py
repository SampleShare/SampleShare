from django.test import TestCase, Client
from .models import *
from django.urls import reverse


#------------------ Data Model & Database Testing-------------------------#
# This section contains a series of tests that tests our data model and database
# to make sure that data is being stored in the database the way its suppose to be
# and to make sure that the data being store can be retrieved/accessed
#
#
#

#This is testing that the samples table in the DB is able to store samples and retreive them
class SampleTableTestCase(TestCase):
    def setUp(self):
        self.testSample = Sample.objects.create(sampleName="Test Sample", audioFile="test.mp3", isPublic=False)

    def test_sample_creation(self):
        # testing to see if the sample created above is in the db
        self.assertEqual(self.testSample.sampleName, "Test Sample")

    def test_sample_retrieval(self):
        obj = Sample.objects.get(sampleName = "Test Sample")
        # tests to see if the sample created can be retrieved
        self.assertEqual(obj, self.testSample)

# Testing to see if the posts table in the DB can store a post and be able to retrieve that data
class PostTableTestCase(TestCase):
    def setUp(self):
        self.testUser = User.objects.create(username="Test User", password = "password123")
        self.testUserProfile = UserProfile.objects.create(user= self.testUser, dateOfBirth = "2020-10-10", numberOfFollowers=0)
        self.testPost = Post.objects.create(postText="Test Post", userProfiles = self.testUserProfile)

    def test_post_creation(self):
        # tests to make sure the post created above is in the db
        self.assertEqual(self.testPost.postText, "Test Post")

         # tests to make sure the post created above is tied to the user profile and the user
        self.assertEqual(self.testPost.userProfiles.user.username, "Test User")

    def test_post_retrieval(self):
        post = Post.objects.get(postText = "Test Post")
        # tests to see if the post created in the db can be retreived
        self.assertEqual(post, self.testPost)

# Testing to see if creating a comment tied to the post is being store and retrieved correctly
class CommentTableTestCase(TestCase):
    def setUp(self):
        testPost = Post.objects.create(postText="Test Post")
        self.testComment = Comment.objects.create(commentMessage="Test Comment", posts=testPost)

    def test_comment_creation(self):
        # tests to see if the comment created is in the db
        self.assertEqual(self.testComment.commentMessage, "Test Comment")

        # tests to see if the comment created is tied to the post
        self.assertEqual(self.testComment.posts.postText, "Test Post")

    def test_comment_retrieval(self):
        comment = Comment.objects.get(commentMessage = "Test Comment")
        
        # tests to see if the comment created can be retrieved from the db
        self.assertEqual(comment, self.testComment)

class UserProfileTableTestCase(TestCase):
    def setUp(self):
        self.testUser = User.objects.create(username="Test User", password = "password123")
        self.testUserProfile = UserProfile.objects.create(user = self.testUser, dateOfBirth = "2020-10-10", bio ="", numberOfFollowers = 0)
    
    def test_userprofile_creation(self):
        # Testing to see if the user profile defined above is being created
        self.assertEqual(self.testUserProfile.dateOfBirth, "2020-10-10")

        # Testing to see if the user profile defined above is tied to the user in the user table
        self.assertEqual(self.testUserProfile.user.username, "Test User")

        # Testing to see if the user profile's default photo is pointing to the right place
        self.assertEqual(self.testUserProfile.userPhoto, "profile_pics/profile_picture_default.jpg")
    
    def test_userprofile_retreival(self):
        userProfile = UserProfile.objects.get(user= self.testUser, dateOfBirth = "2020-10-10", bio ="", numberOfFollowers = 0)
        self.assertEqual(userProfile, self.testUserProfile)

class ChatTableTestCase(TestCase):
    def setUp(self):
        self.testUser = User.objects.create(username="Test User", password = "password123")
        self.testUserProfile = UserProfile.objects.create(user = self.testUser, dateOfBirth = "2020-10-10", bio ="", numberOfFollowers = 0)
        self.testChat = Chat.objects.create(chatName= "Test Chat")
        userProfile = UserProfile.objects.filter(dateOfBirth = "2020-10-10")
        self.testChat.userProfiles.set(userProfile)
    
    def test_chat_creation(self):
        # Checks to See if the Chat is being created in the DB
        self.assertEqual(self.testChat.chatName, "Test Chat")
        
        # Checks to see if the Junction table between User Profiles and Chats is being populated
        self.assertNotEqual(self.testChat.userProfiles, None)
    
    def test_chat_retrieval(self):
        chat = Chat.objects.get(chatName = "Test Chat")
        # checks to see if that chat being created can be retrieved
        self.assertEqual(chat, self.testChat)

class MessageTableTestCase(TestCase):
    def setUp(self):
        self.testUser = User.objects.create(username="Test User", password = "password123")
        self.testChat = Chat.objects.create(chatName= "Test Chat")
        self.testMessage = Message.objects.create(content= "Test Message", user= self.testUser, chat = self.testChat)
    
    def test_message_creation(self):

        # tests to make sure the message being created is in the db
        self.assertEqual(self.testMessage.content, "Test Message")

        # tests to make sure the message being created is tied to the user
        self.assertEqual(self.testMessage.user.username, "Test User")

        # tests to make sure that the message being created is tied to the chat assigned to it
        self.assertEqual(self.testMessage.user.username, "Test User")
    
    def test_message_retrieval(self):
        message = Message.objects.get(content = "Test Message", user= self.testUser, chat = self.testChat)
        # testing to make sure that the message created can be retrieved from the db
        self.assertEqual(message, self.testMessage)


class TestFriendRequestTableTestCase(TestCase):
    def setUp(self):
        self.testUserOne = User.objects.create(username="Test User One", password = "password123")
        self.testUserTwo = User.objects.create(username="Test User Two", password = "password123")
        self.testUserProfileOne = UserProfile.objects.create(user = self.testUserOne, dateOfBirth = "2020-10-10", bio ="", numberOfFollowers = 0)
        self.testUserProfileTwo = UserProfile.objects.create(user = self.testUserTwo, dateOfBirth = "2020-10-10", bio ="", numberOfFollowers = 0)

        self.testFriendReq = FriendRequest.objects.create(from_user = self.testUserProfileOne, to_user = self.testUserProfileTwo)
    
    def test_friend_request_creation(self):
        # Testing to see if the friend request created above is storing the first user correctly
        self.assertEqual(self.testUserProfileOne.user.username, "Test User One")

        # Testing to see if the friend request created above is storing the second user correctly
        self.assertEqual(self.testUserProfileTwo.user.username, "Test User Two")
    
    def test_friend_request_retrieval(self):
        friendRequest = FriendRequest.objects.get(from_user = self.testUserProfileOne, to_user = self.testUserProfileTwo)

        # Testing to see if the friend request created above can be retrieved from the DB
        self.assertEqual(friendRequest, self.testFriendReq)

class TestGenreTableTestCase(TestCase):
    def setUp(self):
        self.testGenre = Genre.objects.create(genreName = "Test Genre")
    
    def test_genre_creation(self):
        # Testing to see if the genre created above is acutally being created in the db
        self.assertEqual(self.testGenre.genreName, "Test Genre")
    
    def test_genre_retrieval(self):
        genre = Genre.objects.get(genreName = "Test Genre")
        # Tests to see if the genre created above can be retrieved from the database
        self.assertEqual(genre, self.testGenre)


#---------------------------------------------------------------------------------------

    