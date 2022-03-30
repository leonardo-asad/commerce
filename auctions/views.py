from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .models import User, Listing, Bid, Comment, Watchlist

from datetime import datetime


def index(request):
    return render(request, "auctions/index.html", {
        'listings': Listing.objects.all()
    })


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
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


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
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

@login_required
def create(request):
    if request.method == "POST":
        if not len(Listing.objects.filter(title=request.POST['title'])) == 0:
            return render(request, "auctions/create.html", {
                'message': "This title already exist. Please use another."
            })

        new_listing = Listing(title=request.POST['title'],
                              description=request.POST['description'],
                              price=request.POST['price'],
                              date= datetime.now(),
                              listed_by=request.user)
        new_listing.save()

        return HttpResponseRedirect(reverse("index"))
        #breakpoint()

    return render(request, "auctions/create.html")

def listings(request, listing_id):

    listing = Listing.objects.get(id=listing_id)

    if request.method == "POST":
        if request.POST['watchlist'] == "add":

            if not len(Watchlist.objects.filter(user=request.user,listing=listing).values()) == 0:
                return render(request, "auctions/listings.html", {
                    "message": "Already in Watchlist",
                    'listing': listing
                })

            watchlist = Watchlist(user=request.user,
                                  listing=listing)

            watchlist.save()

            return HttpResponseRedirect(reverse("watchlist"))

    return render(request, "auctions/listings.html", {
        'listing': listing
    })

@login_required
def watchlist(request):

    watchlist = Watchlist.objects.filter(user=request.user)

    return render(request, "auctions/watchlist.html", {
        'watchlist': watchlist
    })
