from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path('create_listing', views.create_listing, name='create_listing'),
    path('listings/<int:listing_id>', views.listing, name='listing'),
    path('listings/<int:listing_id>/close_listing', views.close_listing, name='close_listing'),
    path('watchlist', views.watchlist, name='watchlist'),
    path('listings/<int:listing_id>/add_watchlist', views.add_watchlist, name='add_watchlist'),
    path('listings/<int:listing_id>/remove_watchlist', views.remove_watchlist, name='remove_watchlist'),
    path('categories', views.categories, name='categories'),
    path('categories/<str:category>', views.category, name='category'),
    path('listings/<int:listing_id>/comment', views.comment, name='comment' )
]
