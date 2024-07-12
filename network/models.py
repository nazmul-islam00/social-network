from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    @property
    def followers(self):
        return self.all_followers.filter(
            is_archived=False
        )
        
    @property
    def following(self):
        return self.all_following.filter(
            is_archived=False
        )
        
    @property
    def likes(self):
        return self.all_likes.filter(
            is_archived=False
        )

class Post(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="posts"
    )
    content = models.TextField()
    timestamp = models.DateTimeField(
        auto_now_add=True
    )
    
    def serialize(self):
        return {
            "id": self.id,
            "user": self.user.username,
            "content": self.content,
            "timestamp": self.timestamp.strftime("%b %d %Y, %I:%M %p"),
            "likes": len(self.likes.all()).__str__()
        }
        
    @property
    def likes(self):
        return self.all_likes.filter(
            is_archived=False
        )
        
class LikeManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_archived=False)
    
class Like(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="all_likes"
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="all_likes"
    )
    timestamp = models.DateTimeField(
        auto_now_add=True
    )
    is_archived = models.BooleanField(
        default=False
    )
    objects = models.Manager()
    active_objects = LikeManager()
    
    def like(self):
        self.is_archived = False
        self.save()
        
    def dislike(self):
        self.is_archived = True
        self.save()
 
class FollowerManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_archived=False)
       
class Follower(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="all_followers"
    )
    follower = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="all_following"
    )
    timestamp = models.DateTimeField(
        auto_now_add=True
    )
    is_archived = models.BooleanField(
        default=False
    )
    objects = models.Manager()
    active_objects = FollowerManager()
    
    def follow(self):
        self.is_archived = False
        self.followed_at = timezone.now()
        self.save()
        
    def unfollow(self):
        self.is_archived = True
        self.save()