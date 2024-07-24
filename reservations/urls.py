from unicodedata import name
from django.urls import path

from .views import *

urlpatterns = [
    
        #path('room-allocations', RoomAllocationsView.as_view(), name='room-allocations'),
        path('room-allocations', RoomAllocationsView.as_view(), name='room-allocations-with-status'),
        path('change-room-status/<int:id>', RoomStatusView.as_view(), name='change-room-status'),
        path('book-room', BookRoomView.as_view(), name='book-room'),
        path('check-user-in', CheckInView.as_view(), name='check-user-in'),
        path('multiple_rooms_check_in', MultipleCheckInView.as_view(), name='multiple_rooms_check_in'),
        path('check-user-out', CheckOutView.as_view(), name='check-user-out'),
        path('single-booking-history/<int:id>', SingleBookingView.as_view(), name='single-booking-history'),
        
        path("room-history/<int:room_id>/", RoomHistoryView.as_view(), name="room_booking_history"),
        
        path('booking-history', BookingsHistoryView.as_view(), name='booking-history'),
        path('booking-history-doc/<str:file_type>', BookingsHistoryDocView.as_view(), name='booking-history-doc'),
        path('current-booking-history', CurrentBookingHistoryView.as_view(), name='current-booking-history'),
        path('user-booking-history/<str:user_id>', UserBookingHistoryView.as_view(), name='user-booking-history'),
        path('dashboard-bootstrap', DashboardBootstrapView.as_view(), name='dashboard-bootstrap'),
        path('room-bootstrap', RoomBootstrapView.as_view(), name='room-bootstrap'),
        path('rooms-for-checkout', RoomsForCheckoutView.as_view(), name='rooms-for-checkout'),
        path('checkout', UserCheckoutView.as_view(), name='checkout'),
    ]