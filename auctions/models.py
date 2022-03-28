from django.contrib.auth.models import AbstractUser
from django.db import models
from models import Model



class User(AbstractUser):
    pass

class Listing(Model):
    date = models.DateField()
    title = models.CharField(max_length=64)
    description = models.TextField()
    price = models.PositiveIntegerField()
    category = models.CharField(max_length=64)
    listed_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="publications")

class Bid(Model):
    date = models.DateField()
    bid = models.PositiveIntegerField()
    bid_author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_bids")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="listing_bids")

class Comment(Model):
    comment = models.TextField()
    date = models.DateField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_comments")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="listing_comments")
