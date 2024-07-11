from django.contrib import admin
from .models import Booking, RoomAllocation, RoomStatusChange
# Register your models here.

admin.site.register(RoomAllocation)
admin.site.register(RoomStatusChange)


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'room']
