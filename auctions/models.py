from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    pass

class Listing(models.Model):
    date = models.DateField()
    title = models.CharField(max_length=64)
    description = models.TextField()
    price = models.PositiveIntegerField()
    category = models.CharField(max_length=64)
    listed_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="publications")

    def __str__(self):
        return f"Listing title: {self.title}. Created on {self.date}."

class Bid(models.Model):
    date = models.DateField()
    bid = models.PositiveIntegerField()
    bid_author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_bids")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="listing_bids")

    def __str__(self):
        return f"Bid made by: {self.bid_author}. Created on {self.date}."

class Comment(models.Model):
    comment = models.TextField()
    date = models.DateField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_comments")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="listing_comments")

    def __str__(self):
        return f"Comment made by: {self.author}. Created on {self.date}."
