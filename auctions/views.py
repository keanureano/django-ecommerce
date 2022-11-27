from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import *


def index(request):
    categories = Category.objects.all()
    selected_category = request.GET.get("category")
    if selected_category == "All":
        return redirect("index")
    elif selected_category != None:
        category = Category.objects.get(name=selected_category)
        listings = Listing.objects.filter(is_active=True, category=category)
    else:
        listings = Listing.objects.filter(is_active=True)
    print(listings)
    return render(request, "auctions/index.html", {
        "listings": listings,
        "categories": categories,
        "selected_category": selected_category
    })

def listing(request, listing_id):
    user = request.user
    listing = Listing.objects.get(id=listing_id)
    comments = Comment.objects.filter(listing=listing_id).order_by("-date_commented")
    highest_bid = Bid.objects.filter(listing = listing_id).order_by('-price').first()
    if request.method == "POST":
        watchlist = request.POST["watchlist"]
        if watchlist == "add":
            listing.watchlist.add(user)
        elif watchlist == "remove":
            listing.watchlist.remove(user)
        elif watchlist == "remove2":
            listing.watchlist.remove(user)
            return redirect("watchlist")
        return redirect("listing", listing_id)
    else:
        is_watchlisted = (user in listing.watchlist.all())
        return render(request, "auctions/listing.html", {
            "listing": listing,
            "highest_bid": highest_bid,
            "is_watchlisted": is_watchlisted,
            "comments": comments
        })
        

@login_required
def create_listing(request):
    if request.method == "POST":
        try:
            # Try to create listing
            listing = Listing(
                title = request.POST["title"],
                description = request.POST["description"],
                starting_price = float(request.POST["starting_price"]),
                image_url = request.POST["image_url"],
                category = Category.objects.get(id=int(request.POST["category"])),
                author = request.user
            )
            listing.save()
            # Try to create bid            
            bid = Bid(
                author = request.user,
                listing = listing,
                bid = float(request.POST["starting_price"])
            )
            bid.save()
            messages.success(request, "Succesfully added listing!")
        except Exception as e:
            messages.error(request, f"Failed to create listing. {e}")
            return redirect("create")
        return redirect("index")
    else:
        return render(request, "auctions/create.html", {
            "categories": Category.objects.all()
        })

@login_required
def create_comment(request, listing_id):
    if request.method == "POST":
        try:
            user_comment = request.POST["comment"]
            if user_comment == "" or user_comment.isspace():
                raise ValueError("Comment must not be empty")
            comment = Comment(   
                author = request.user,
                listing = Listing.objects.get(id=listing_id),
                comment = user_comment,
            )
            comment.save()
            messages.success(request, "Successfully added comment!")
        except Exception as e:
            messages.error(request, f"Failed to create comment. {e}")
            return redirect("listing", listing_id)
        return redirect("listing", listing_id)
    else:
        pass

@login_required
def delete_comment(request, listing_id):
    if request.method == "POST":
        try:
            comment_id = request.POST["comment_id"]
            if comment_id == "" or comment_id.isspace():
                raise ValueError("Comment is empty")
            comment = Comment.objects.get(id=comment_id)
            comment.delete()
            messages.success(request, "Successfully deleted comment!")
        except Exception as e:
            messages.error(request, f"Failed to delete comment. {e}")
            return redirect("listing", listing_id)
        return redirect("listing", listing_id)
    else:
        pass
    
@login_required
def add_bid(request, listing_id):
    if request.method == "POST":
        author = request.user
        listing = Listing.objects.get(id=listing_id)
        highest_bid = Bid.objects.filter(listing=listing).order_by("-price").first()
        bid_price = float(request.POST["bid_price"])
        try:
            if bid_price <= highest_bid.price:
                raise ValueError("Bid is less than the minimum bid.")
            bid = Bid(
                author = author,
                listing = listing,
                price = bid_price
            )
            bid.save()
            messages.success(request, "Successfully added bid!")
        except Exception as e:
            messages.error(request, f"Failed to add bid. {e}")
            return redirect("listing", listing_id)
        return redirect("listing", listing_id)
    else:
        pass

def watchlist(request):
    user = request.user
    listings = Listing.objects.filter(watchlist=user)
    if not listings:
        messages.warning(request, "No listings in the watchlist.")
    return render(request, "auctions/watchlist.html", {
        "listings": listings
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
            messages.error(request, "Invalid username and/or password.")
            return render(request, "auctions/login.html")
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
        if not username or not email or not password or password != confirmation:
            if not username:
                messages.error(request, "Must have a username.")
            if not email:
                messages.error(request, "Must have an email.")
            if not password:
                messages.error(request, "Must have a password.")
            if password != confirmation:
                messages.error(request, "Passwords must match.")
            return render(request, "auctions/register.html")

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError as e:
            messages.error(request, "Username is already taken.")
            return render(request, "auctions/register.html")
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
