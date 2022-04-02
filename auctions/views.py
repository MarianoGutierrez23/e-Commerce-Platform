from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
from datetime import datetime

from .models import *


class NewListingForm(forms.Form):
    title = forms.CharField(label='Title')
    description = forms.CharField(widget=forms.Textarea, label='Product Description')
    bid = forms.FloatField(label='Starting Bid')
    image = forms.URLField(label='Image URL')

    categories = (
        ('',''),
        ('Electronic Devices', 'Electronic Devices'),
        ('Instruments','Instruments'),
        ('Outdoors & Travel Gear','Outdoors & Travel Gear'),
    )
    category = forms.ChoiceField(label='Category',choices=categories)

    title.widget.attrs.update({'class': 'form-control'})
    description.widget.attrs.update({'class': 'form-control'})
    bid.widget.attrs.update({'class': 'form-control'})
    image.widget.attrs.update({'class': 'form-control'})
    category.widget.attrs.update({'class': 'form-control'})





def index(request):
    active_listings = Listing.objects.filter(active=True)

    return render(request, "auctions/index.html", {
        'listings': active_listings
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
def create_listing(request):
    if request.method == 'POST':
        form = NewListingForm(request.POST)
    
        user = request.user
        
        # Check if form data is valid (server-side)
        if form.is_valid():
            
            title = form.cleaned_data['title']
            description = form.cleaned_data['description']
            bid = form.cleaned_data['bid']
            image = form.cleaned_data['image']
            category = form.cleaned_data['category']

            # Create Listing
            new_listing = Listing()

            new_listing.creator = user
            new_listing.title = title
            new_listing.description = description
            new_listing.current_bid = bid
            new_listing.image = image
            new_listing.category = category

            new_listing.save()


            new_bid = Bid(user=user, listing=new_listing, price=bid)
            new_bid.save()


            return HttpResponseRedirect(reverse('index'))

        else:
            
            return HttpResponseRedirect(reverse("create_listing"))
    
    return render(request, 'auctions/create_listing.html', {
        'form': NewListingForm()
    })

def listing(request,listing_id):
    listing = Listing.objects.get(id=listing_id)
    in_watchlist = False
    comments = False
    

    if request.method == 'POST':
        bid = request.POST['bid']
        new_bid = Bid(user=request.user,listing=listing,price=bid)
        new_bid.save()

        listing.current_bid = bid
        listing.save()
        
        messages.success(request,'Your bid has been placed!')
        return HttpResponseRedirect(reverse('listing',kwargs={
            'listing_id': listing_id
        }))
    
    # for counting total bids on a particular listing
    total_bids = Bid.objects.filter(listing=listing)

    # for getting user who placed current bid
    current_bid = total_bids.latest('date')

    # check if listing is in already in user's watchlist
    try:
        watchlist = Favorite.objects.filter(user=request.user).values('listing')

        for favorite in watchlist:
            if favorite['listing'] == listing_id:
                in_watchlist = True
                break
    # except user is not authenticated
    except Exception:
        pass
    
    # get comments
    try:
        listing_comments = Comment.objects.filter(listing=listing)
        comments = listing_comments
    # except there is no comments for that listing    
    except Exception:
        pass



    return render(request, 'auctions/listing.html', {
        'listing': listing,
        'total_bids': len(total_bids),
        'current_bid': current_bid,
        'in_watchlist': in_watchlist,
        'comments': comments
        
    })

def close_listing(request,listing_id):
    listing = Listing.objects.get(id=listing_id)
    
    listing.active = False
    listing.save()

    return HttpResponseRedirect(reverse('listing', kwargs={
        'listing_id': listing_id
    }))

def watchlist(request):
    favorites = Favorite.objects.filter(user=request.user)

    return render(request, 'auctions/watchlist.html', {
        'favorites': favorites
    })

def add_watchlist(request,listing_id):
    listing = Listing.objects.get(id=listing_id)
    user = request.user

    new_favorite = Favorite(user=user, listing=listing)
    new_favorite.save()

    messages.success(request, 'Listing successfully added to Watchlist!')
    return HttpResponseRedirect(reverse('listing', kwargs={
        'listing_id': listing_id
    }))

def remove_watchlist(request, listing_id):
    listing = Listing.objects.get(id=listing_id)

    Favorite.objects.filter(listing=listing).delete()
    messages.success(request, 'Listing successfully removed from Watchlist.')
    return HttpResponseRedirect(reverse('listing', kwargs={
        'listing_id': listing_id
    }))

def categories(request):
    categories = Listing.objects.all().values('category')

    categories_listed = []

    for category in categories:
        if category['category'] in categories_listed:
            continue
        else:
            categories_listed.append(category['category'])

    return render(request, 'auctions/categories.html', {
        'categories': categories_listed
    })

def category(request, category):
    listings = Listing.objects.filter(active=True).filter(category=category)

    return render(request, 'auctions/category.html', {
        'listings': listings,
        'category': category
    })

def comment(request, listing_id):
    if request.method == 'POST':
        listing = Listing.objects.get(id=listing_id)
        comment = request.POST['comment']
        time = datetime.now()

        time_str = time.strftime("%m/%d/%y  %H:%M")

        new_comment = Comment(user=request.user, time=time_str, listing=listing, text=comment)
        new_comment.save()

        return HttpResponseRedirect(reverse('listing', kwargs={
            'listing_id': listing_id
        }))