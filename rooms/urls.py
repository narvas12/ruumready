from unicodedata import name
from django.urls import path

from .views import *

urlpatterns = [
        #ROOMS ROUTE
        path('create-room', RoomCreateView.as_view(), name='create-room'),
        path('room/<int:id>', RoomView.as_view(), name='room'),
        #path('rooms', RoomsView.as_view(), name='rooms'),
        path('rooms', RoomsView.as_view(), name='rooms'),
        path('room-update/<int:id>', RoomUpdateView.as_view(), name='room-update'),
        path('room-delete/<int:id>', RoomDeleteView.as_view(), name='room-delete'),
        
        #APARTMENT TYPE ROUTE
        path('create-apartment-type', ApartmentTypeCreateView.as_view(), name='create-apartment-type'),
        path('apartment-type/<int:id>', ApartmentTypeView.as_view(), name='apartment-type'),
        path('apartment-types/', ApartmentTypesView.as_view(), name='apartment-types'),
        path('apartment-type-update/<int:id>', ApartmentTypeUpdateView.as_view(), name='apartment-type-update'),
        path('apartment-type-delete/<int:id>', ApartmentTypeDeleteView.as_view(), name='apartment-type-delete'),
    ]