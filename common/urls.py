from unicodedata import name
from django.urls import path

from .views import (
        RatingCreateView,
        RatingsView
       )
from rest_framework_simplejwt.views import (TokenRefreshView,)

urlpatterns = [
    
        #RATING ROUTES
        path('ratings/create-rating', RatingCreateView.as_view(), name='create-rating'),
        path('ratings/ratings', RatingsView.as_view(), name='ratings')
    
    ]