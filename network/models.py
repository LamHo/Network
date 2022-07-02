from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):    
    followers = models.ManyToManyField("User", related_name="followings")

class Post(models.Model):
    content = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    likers = models.ManyToManyField("User", related_name="liked_posts")

    def serialize(self):
        return {
            "id": self.id,
            "creator": self.creator.username,
            "content": self.content,
            "timestamp": self.timestamp.strftime("%b %d %Y, %I:%M %p"),
            "likes": self.likers.count(),
            "likers": [user.username for user in self.likers.all()]
        }


