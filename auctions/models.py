from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    pass

class Listing(models.Model):
    title = models.CharField(max_length=64)
    active = models.BooleanField(default=True)
    description = models.TextField()
    image = models.URLField()
    price = models.PositiveIntegerField()
    category = models.CharField(max_length=64)
    listed_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="publications")
    date = models.DateField()

    def __str__(self):
        return f"Id: {self.id}. Title: {self.title}. Created on {self.date}."

class Bid(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="listing_bids")
    bid = models.PositiveIntegerField()
    bid_author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_bids")
    date = models.DateField()

    def __str__(self):
        return f"Id: {self.id}. Made by: {self.bid_author}. Created on {self.date}."

class Comment(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="listing_comments")
    comment = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_comments")
    date = models.DateField()

    def __str__(self):
        return f"Id: {self.id}. Made by: {self.author}. Created on {self.date}."

class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="followers")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="followers")
