

from django.contrib.auth.models import AbstractUser
from django.db import models



class User(AbstractUser):
    pass

class Listing(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    description = models.TextField()
    current_bid = models.FloatField()
    category = models.CharField(max_length=30)
    image = models.CharField(max_length=200)
    active = models.BooleanField(default=True)


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    time = models.CharField(max_length=30,default='time')
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    text = models.TextField()
    

    
    
class Bid(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    price = models.FloatField()
    date = models.DateTimeField(auto_now=True)

class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)