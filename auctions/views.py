from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .models import User, Listing, Bid, Comment, Watchlist
from .forms import BidForm, CommentForm, ListingForm

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


def get_current_price(listing):
    # Filter bids in order to get the current price of the listing
    bids = Bid.objects.filter(listing=listing).values()

    if len(bids) == 0:
        return listing.price
    return max([bid['bid'] for bid in bids])

def get_comments(listing):
    # Filter listing comments
    comments = Comment.objects.filter(listing=listing)

    if len(comments) == 0:
        return None
    return comments


def listings(request, listing_id):

    # Lookup the listing data in the model database
    listing = Listing.objects.get(id=listing_id)

    # Filter who watchlisted this post
    watchlists = Watchlist.objects.filter(listing=listing).values()
    watchlists_users = [watchlist['user_id'] if not len(watchlists) == 0 else '' for watchlist in watchlists]

    if request.method == "POST":

        # Add listing to watchlist
        if "add_watchlist" in request.POST:

            if not len(Watchlist.objects.filter(user=request.user,listing=listing).values()) == 0:
                return render(request, "auctions/listings.html", {
                    "message": "Already in Watchlist. Press the buttom to remove from it",
                    'listing': listing
                })

            watchlist = Watchlist(user=request.user,
                                  listing=listing)

            watchlist.save()

            # Filter who watchlisted this post
            watchlists = Watchlist.objects.filter(listing=listing).values()
            watchlists_users = [watchlist['user_id'] if not len(watchlists) == 0 else '' for watchlist in watchlists]

            return render(request, "auctions/listings.html", {
                'listing': listing,
                'message': "Succesfully added to Watchlist!",
                'watchlists': watchlists_users,
                'current_price': get_current_price(listing),
                'comments': get_comments(listing),
                'bid_form': BidForm(),
                'comment_form': CommentForm()
            })

        # Remove listing from watchlist
        if "remove_watchlist" in request.POST:

            watchlist = Watchlist.objects.get(user=request.user,listing=listing)

            watchlist.delete()

            return render(request, "auctions/listings.html", {
                'listing': listing,
                'message': "Succesfully removed from Watchlist",
                'current_price': get_current_price(listing),
                'comments': get_comments(listing),
                'bid_form': BidForm(),
                'comment_form': CommentForm()
            })

        # Place Bid
        if "bid" in request.POST:

            bid_form = BidForm(request.POST)

            if bid_form.is_valid():

                bid = bid_form.cleaned_data['bid']

                if not bid >= listing.price:
                    return render(request, "auctions/listings.html", {
                        'listing': listing,
                        'message': f"The bid must be at least the starting price of ${listing.price} USD",
                        'current_price': get_current_price(listing),
                        'bid_form': BidForm(),
                        'comments': get_comments(listing),
                        'comment_form': CommentForm()
                        })

                previous_bids = Bid.objects.filter(listing=listing).values()

                if not len(previous_bids) == 0:
                    for previous_bid in previous_bids:
                        if previous_bid['bid'] >= bid:
                            return render(request, "auctions/listings.html", {
                                    'listing': listing,
                                    'message': "The bid must be greater than any bid that has been placed",
                                    'current_price': get_current_price(listing),
                                    'bid_form': BidForm(),
                                    'comments': get_comments(listing),
                                    'comment_form': CommentForm()
                                    })

                bid_object = Bid(listing=listing,
                                bid=bid,
                                bid_author=request.user,
                                date=datetime.now())

                bid_object.save()

                return render(request, "auctions/listings.html", {
                        'listing': listing,
                        'message': "Bid placed succesfully",
                        'current_price': get_current_price(listing),
                        'bid_form': BidForm(),
                        'comments': get_comments(listing),
                        'comment_form': CommentForm()
                    })

            return render(request, "auctions/listings.html", {
                        'listing': listing,
                        'current_price': get_current_price(listing),
                        'bid_form': bid_form,
                        'comments': get_comments(listing),
                        'comment_form': CommentForm()
                    })

        # Close Auction
        if "close_auction" in request.POST:
            bids = Bid.objects.filter(listing=listing).values()

            if len(bids) == 0:
                return render(request, "auctions/listings.html", {
                    'listing': listing,
                    'message': "Cannot close the Auction because there is no placed bid yet",
                    'current_price': get_current_price(listing),
                    'bid_form': BidForm,
                    'comments': get_comments(listing),
                    'comment_form': CommentForm()
                })

            max_bid = sorted(bids, key=lambda x: x['bid'], reverse=True)[0]

            winner = User.objects.get(pk=max_bid['bid_author_id'])

            Listing.objects.filter(pk=listing_id).update(active=False, winner=winner, winning_bid=max_bid['bid'])

            listing = Listing.objects.get(pk=listing_id)

            return render(request, "auctions/listings.html", {
                    'listing': listing,
                    'bid_form': bid_form,
                    'comments': get_comments(listing)
                })

        if 'comment' in request.POST:
            comment_form = CommentForm(request.POST)

            if comment_form.is_valid():

                comment=comment_form.cleaned_data['comment']

                comment = Comment(listing=listing,
                                  comment=comment,
                                  author=request.user,
                                  date=datetime.now())
                comment.save()

                return render(request, "auctions/listings.html", {
                    'listing': listing,
                    'watchlists': watchlists_users,
                    'current_price': get_current_price(listing),
                    'bid_form': BidForm(),
                    'comments': get_comments(listing),
                    'comment_form': CommentForm()})

            return render(request, "auctions/listings.html", {
                    'listing': listing,
                    'watchlists': watchlists_users,
                    'current_price': get_current_price(listing),
                    'bid_form': BidForm(),
                    'comments': get_comments(listing),
                    'comment_form': comment_form})


    return render(request, "auctions/listings.html", {
        'listing': listing,
        'watchlists': watchlists_users,
        'current_price': get_current_price(listing),
        'bid_form': BidForm(),
        'comments': get_comments(listing),
        'comment_form': CommentForm()
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
