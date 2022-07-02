
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("new_post", views.new_post, name="new_post"),
    path("createPost", views.createPost, name="createPost"),
    path("all_posts", views.all_posts, name="all_posts"),
    path("profile/<str:name>", views.profile, name="profile"),  
    path("following", views.following, name="following"),

    #API routes:
    path("posts", views.posts, name="posts"), #return all or some posts in json
    path("post/<int:id>", views.post, name="post"), #return a specific post in json
    path("postsOf/<str:name>", views.postsOf, name="postsOf"), #return all posts of a specific user in json
    path("followingPosts", views.followingPosts, name="followingPosts") #return all posts of the users that request user are folowing
]
