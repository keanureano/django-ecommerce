from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("create", views.create_listing, name="create"),
    path("listing/<int:listing_id>", views.listing, name="listing"),
    path("create_comment/<int:listing_id>", views.create_comment, name="create_comment"),
    path("delete_comment/<int:listing_id>", views.delete_comment, name="delete_comment"),
    path("add_bid/<int:listing_id>", views.add_bid, name="add_bid"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register")
]
