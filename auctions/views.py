from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .models import User, Listing, Bid, Comment, Watchlist
from .forms import ListingForm

from datetime import datetime


def index(request):
    return render(request, "auctions/index.html", {
        'listings': Listing.objects.filter(active=True)
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

        form = ListingForm(request.POST)

        if form.is_valid():

            new_listing = Listing(title=form.cleaned_data['title'],
                                image=form.cleaned_data['image'],
                                description=form.cleaned_data['description'],
                                category=form.cleaned_data['category'],
                                price=form.cleaned_data['price'],
                                date= datetime.now(),
                                listed_by=request.user)
            new_listing.save()

            return HttpResponseRedirect(reverse("index"))

        else:
            return render(request, "auctions/create.html", {
                'form': form
            })

    return render(request, "auctions/create.html", {
        'form': ListingForm()
    })

def listings(request, listing_id):

    listing = Listing.objects.get(id=listing_id)

    if request.method == "POST":
        # Add listing to watchlist
        if request.POST['listings'] == "add_watchlist":

            if not len(Watchlist.objects.filter(user=request.user,listing=listing).values()) == 0:
                return render(request, "auctions/listings.html", {
                    "message": "Already in Watchlist. Press the buttom to remove from it",
                    'listing': listing
                })

            watchlist = Watchlist(user=request.user,
                                  listing=listing)

            watchlist.save()

            return HttpResponseRedirect(reverse("watchlist"))

        # Remove listing from watchlist
        if request.POST['listings'] == "remove_watchlist":

            watchlist = Watchlist.objects.get(user=request.user,listing=listing)

            watchlist.delete()

            return render(request, "auctions/listings.html", {
                'listing': listing
            })

        # Place Bid
        if request.POST['listings'] == "place_bid":
            bid = int(request.POST['bid'])

            if not bid >= listing.price:
                return render(request, "auctions/listings.html", {
                    'listing': listing,
                    'message': f"The bid must be at least the starting price of ${listing.price} USD"
                    })

            previous_bids = Bid.objects.filter(listing=listing).values()

            if not len(previous_bids) == 0:
                for previous_bid in previous_bids:
                    if previous_bid['bid'] >= bid:
                        return render(request, "auctions/listings.html", {
                                'listing': listing,
                                'message': "The bid must be greater than any bid that has been placed"
                                })

            bid_object = Bid(listing=listing,
                             bid=bid,
                             bid_author=request.user,
                             date=datetime.now())

            bid_object.save()

            return render(request, "auctions/listings.html", {
                    'listing': listing,
                    'message': "Bid placed succesfully"
                })

        # Close Auction
        if request.POST['listings'] == "close_auction":
            bids = Bid.objects.filter(listing=listing).values()

            if len(bids) == 0:
                return render(request, "auctions/listings.html", {
                    'listing': listing,
                    'message': "Cannot close de Auction because there is no placed bid yet"
                })

            max_bid = sorted(bids, key=lambda x: x['bid'], reverse=True)[0]

            winner = User.objects.get(pk=max_bid['bid_author_id'])

            Listing.objects.filter(pk=listing_id).update(active=False, winner=winner, winning_bid=max_bid['bid'])

            listing = Listing.objects.get(pk=listing_id)

            return render(request, "auctions/listings.html", {
                    'listing': listing,
                    'message': f"Auction closed succesfully. Winner {listing.winner}. Price ${listing.winning_bid} USD"
                })

    return render(request, "auctions/listings.html", {
        'listing': listing
    })

@login_required
def watchlist(request):

    watchlist = Watchlist.objects.filter(user=request.user)

    return render(request, "auctions/watchlist.html", {
        'watchlist': watchlist
    })

def categories(request):

    listings = Listing.objects.all().values()

    categories = []

    for listing in listings:
        if not listing['category'] in categories and not listing['category'] == '':
            categories.append(listing['category'])

    return render(request, "auctions/categories.html", {
        'categories': categories
    })


def by_category(request, category):

    listings = Listing.objects.filter(category=category, active=True)

    return render(request, "auctions/by_category.html", {
        'listings': listings,
        'category': category
    })
