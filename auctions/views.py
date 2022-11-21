from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import User, Category, Listing


def index(request):
    categories = Category.objects.all()
    selected_category = request.GET.get("category")
    if selected_category == "All":
        return redirect("index")
    elif selected_category != None:
        category = Category.objects.get(name=selected_category)
        listings = Listing.objects.filter(is_active=True, category_id=category)
    else:
        listings = Listing.objects.filter(is_active=True)
    return render(request, "auctions/index.html", {
        "listings": listings,
        "categories": categories,
        "selected_category": selected_category
    })

@login_required
def create_listing(request):
    if request.method == "POST":
        # Try to save listing
        try:
            listing = Listing(
            title = request.POST["title"],
            description = request.POST["description"],
            starting_price = float(request.POST["starting_price"]),
            image_url = request.POST["image_url"],
            category_id = Category.objects.get(id=int(request.POST["category_id"])),
            user_id = request.user
        )
            listing.save()
            messages.success(request, "Succesfully added listing!")
        except Exception as e:
            messages.error(request, f"Failed to create listing. {e}")
            return redirect("create")
        return redirect("index")
    else:
        return render(request, "auctions/create.html", {
            "categories": Category.objects.all()
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
