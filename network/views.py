from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
import json

from .models import User, Post, Like, Follower
from .forms import NewPostForm


def index(request):
    if request.method == "GET":
        paginator = Paginator([
            post.serialize()
            for post in Post.objects.order_by("-timestamp").all()
        ], 10)
        page_number = request.GET.get("page", 1)
        
        try:
            page_number = int(page_number)
        except ValueError:
            page_number = 1
        
        if page_number > paginator.num_pages:
            page_number = paginator.num_pages
            
        page = paginator.get_page(page_number)
        
        return render(request, "network/index.html", {
            "page": get_paginator_json(page),
            "posts": json.dumps(list(page)),
            "liked_posts": (
                [] if not request.user.is_authenticated
                else [
                    like.post.id 
                    for like in request.user.likes.all()
                ]
            ),
            "newPostForm": NewPostForm()
        })
        
    return JsonResponse({
        "error": "Invalid request method."
    }, status=400)

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

@login_required(login_url="/login")
def make_post(request):
    if request.method == "POST":
        form = NewPostForm(request.POST)
       
        if form.is_valid():
            post = Post(
                user=request.user,
                content=form.cleaned_data["content"]
            )
            post.save()
            
        return redirect("/")
        
    return JsonResponse({
        "error": "Invalid request method."
    }, status=400)
     
def user(request, username):
    if request.method == "GET":
        user = User.objects.get(
            username=username
        )
        paginator = Paginator([
            post.serialize()
            for post in Post.objects.filter(
                user=user
            ).order_by("-timestamp").all()
        ], 10)
        page_number = request.GET.get("page", 1)
        
        try:
            page_number = int(page_number)
        except ValueError:
            page_number = 1
        
        if page_number > paginator.num_pages:
            page_number = paginator.num_pages
            
        page = paginator.get_page(page_number)
        
        return render(request, "network/user.html", {
            "profileUser": user,
            "page": get_paginator_json(page),
            "posts": json.dumps(list(page)),
            "liked_posts": (
                [] if not request.user.is_authenticated
                else [
                    like.post.id 
                    for like in request.user.likes.all()
                ]
            ),
            "follow": (
                True if not request.user.is_authenticated
                else None if request.user == user
                else False if len(Follower.active_objects.filter(
                    user=user,
                    follower=request.user
                )) > 0
                else True
            )
        })
        
    return JsonResponse({
        "error": "Invalid request method."
    }, status=400)
   
@login_required(login_url="/login") 
def follow(request, username):
    if request.method == "POST":
        user = User.objects.get(
            username=username
        )
        
        try:
            # check if archived Follower object exists
            follower = Follower.objects.get(
                user=user,
                follower=request.user
            )
            
        except Follower.DoesNotExist:
            follower = Follower(
                user=user,
                follower=request.user
            )
            follower.save()
            
        else:
            follower.follow()
            
        return JsonResponse({
            "followers": len(user.followers.all()).__str__(),
            "msg": "followed successfully."
        }, status=201)
        
    return JsonResponse({
        "error": "Invalid request method."
    }, status=400)
    
@login_required(login_url="/login")
def unfollow(request, username):
    if request.method == "POST":
        user = User.objects.get(
            username=username
        )
        
        # archive Follower object
        follower = Follower.objects.get(
            user=user,
            follower=request.user
        )
        follower.unfollow()
        
        return JsonResponse({
            "followers": len(user.followers.all()).__str__(),
            "msg": "unfollowed successfully."
        }, status=201)
        
    return JsonResponse({
        "error": "Invalid request method."
    }, status=400)
    
@login_required(login_url="/login")
def following(request):
    if request.method == "GET":
        paginator = Paginator([
            post.serialize()
            for post in sorted([
                post
                for following in request.user.following.all()
                for post in following.user.posts.all()
            ], key=lambda post: post.timestamp, reverse=True)
        ], 10)
        page_number = request.GET.get("page", 1)
        
        try:
            page_number = int(page_number)
        except ValueError:
            page_number = 1
        
        if page_number > paginator.num_pages:
            page_number = paginator.num_pages
            
        page = paginator.get_page(page_number)
        
        return render(request, "network/following.html", {
            "page": get_paginator_json(page),
            "posts": json.dumps(list(page)),
            "liked_posts": (
                [] if not request.user.is_authenticated
                else [
                    like.post.id 
                    for like in request.user.likes.all()
                ]
            )
        })
        
    return JsonResponse({
        "error": "Invalid request method."
    }, status=400)
    
def get_paginator_json(page):
    return json.dumps({
        "has_previous": page.has_previous(),
        "has_next": page.has_next(),
        "number": page.number,
        "paginator": {
            "num_pages": page.paginator.num_pages
        }
    })
    
@login_required(login_url="/login")
def edit(request, post_id):
    if request.method == "POST":
        post = Post.objects.get(
            id=post_id
        )
        post.content = json.loads(request.body.decode("utf-8")).get("content")
        post.save()
        
        return JsonResponse({
            "msg": "Post edited succeddfully."
        }, status=201)
        
    return JsonResponse({
        "error": "Invalid request method."
    }, status=400)
    
@login_required(login_url="/login")
def like(request, post_id):
    if request.method == "POST":
        post = Post.objects.get(
            id=post_id
        )
        
        
        try:
            # check if archived Like object exists
            like = Like.objects.get(
                user=request.user,
                post=post
            )
            
        except Like.DoesNotExist:
            like = Like(
                user=request.user,
                post=post
            )
            like.save()
            
        else:
            like.like()
            
            
        return JsonResponse({
            "likes": len(post.likes.all()).__str__(),
            "msg": "liked successfully."
        }, status=201)
        
    return JsonResponse({
        "error": "Invalid request method."
    }, status=400)
    
@login_required(login_url="/login")
def dislike(request, post_id):
    if request.method == "POST":
        post = Post.objects.get(
            id=post_id
        )
        
        # archive Like object
        like = Like.objects.get(
            user=request.user,
            post=post
        )
        like.dislike()
        
        return JsonResponse({
            "likes": len(post.likes.all()).__str__(),
            "msg": "disliked successfully."
        }, status=201)
        
    return JsonResponse({
        "error": "Invalid request method."
    }, status=400)