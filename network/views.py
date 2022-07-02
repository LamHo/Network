from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json


from .models import User, Post


def index(request):
    return render(request, "network/index.html")


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")

@login_required(login_url='login')
def new_post(request):
    return render(request, "network/new_post.html")


def all_posts(request):    
    return render(request, "network/all_posts.html")


@csrf_exempt
def profile(request,name):
    if (request.method == "PUT"): #API
        
        data = json.loads(request.body)
        
        if data.get("name") is not None and data.get("action") is not None:
            if data["action"] == "Follow":
                
                followed_user = User.objects.get(username = data["name"])
                request.user.followings.add(followed_user)
            else: #unfollow    
                unfollowed_user = User.objects.get(username = data["name"])
                request.user.followings.remove(unfollowed_user)      
    
    user = User.objects.get(username=name)    
    followers_num = user.followers.count()
    followings_num = user.followings.count()
    is_visiter = not (request.user.username == name)
    if request.user.is_authenticated:
        is_following = request.user.followings.filter(username=name)
        return render(request,"network/profile.html",{
            "name": name,
            "followers_num": followers_num,
            "followings_num": followings_num,
            "is_visiter": is_visiter,
            "is_following": is_following 
        })
    else:
        return render(request,"network/profile.html",{
            "name": name,
            "followers_num": followers_num,
            "followings_num": followings_num,
            "is_visiter": is_visiter
            
        })


@login_required(login_url='login')
def following(request):
    followings = request.user.followings.all()
    names = []
    for person in followings:
        names += [person.username]
    return render(request, "network/following.html",{
        "names": names
    })

#APIs:

@csrf_exempt
@login_required(login_url='login')
def createPost(request):
    # Write a new post must be via POST
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)
        
    data = json.loads(request.body)
    content = data.get("content", "")
    post = Post(content=content, creator=User.objects.get(pk = request.user.id))
    post.save()
    return JsonResponse({"message": "Posted successfully."}, status=201)

def posts(request): #return posts in json
    posts = Post.objects.order_by("-timestamp").all()
    
    
   
    if (request.GET.get("start") is None and request.GET.get("end") is None):
        return JsonResponse([post.serialize() for post in posts], safe=False)
    elif (request.GET.get("start") is None or request.GET.get("end") is None):
        return JsonResponse({"Error": "start or end not found."}, status=404)

    # Get start and end points
    start = int(request.GET.get("start"))
    end = int(request.GET.get("end"))
    # Generate list of posts
    data = []
    for i in range(start, end + 1):
        data.append(posts[i])

    # Artificially delay speed of response
    #time.sleep(1)

    # Return list of posts   
    return JsonResponse([post.serialize() for post in data], safe=False)

@csrf_exempt  
def post(request,id):
    if (request.method == "GET"):
        post = Post.objects.get(id=id)
        return JsonResponse(post.serialize(),safe = False)
    elif(request.method == "PUT"):
        post = Post.objects.get(id = id)
        data = json.loads(request.body)
        if data.get("new_content") is not None:
            post.content = data["new_content"]
        if data.get("action") is not None:
            if (data["action"] == "Like"):
                post.likers.add(request.user)
            else: #Unlike
                post.likers.remove(request.user)
        
        post.save()
        return JsonResponse(post.serialize(),safe = False)


def postsOf(request,name): #return all posts of a specific user in json
    posts = User.objects.get(username=name).posts.order_by("-timestamp").all()

    if (request.GET.get("start") is None and request.GET.get("end") is None):
        return JsonResponse([post.serialize() for post in posts], safe=False)
    elif (request.GET.get("start") is None or request.GET.get("end") is None):
        return JsonResponse({"Error": "start or end not found."}, status=404)

    # Get start and end points
    start = int(request.GET.get("start"))
    end = int(request.GET.get("end"))
    # Generate list of posts
    data = []
    for i in range(start, end + 1):
        data.append(posts[i])

    # Artificially delay speed of response
    #time.sleep(1)

    # Return list of posts   
    return JsonResponse([post.serialize() for post in data], safe=False)
    

@login_required(login_url='login')
def followingPosts(request): #return all posts of the users that request user are folowing
    following_users = request.user.followings.all()
    names = [user.username for user in following_users]
    all_posts = Post.objects.order_by("-timestamp").all()

    following_posts = []

    for post in all_posts:
        if post.creator.username in names:
            following_posts.append(post)

    if (request.GET.get("start") is None and request.GET.get("end") is None):
        return JsonResponse([post.serialize() for post in following_posts], safe=False)
    elif (request.GET.get("start") is None or request.GET.get("end") is None):
        return JsonResponse({"Error": "start or end not found."}, status=404)

    # Get start and end points
    start = int(request.GET.get("start"))
    end = int(request.GET.get("end"))
    # Generate list of posts
    data = []
    for i in range(start, end + 1):
        data.append(following_posts[i])

    # Artificially delay speed of response
    #time.sleep(1)

    # Return list of posts
    return JsonResponse([post.serialize() for post in data], safe=False)