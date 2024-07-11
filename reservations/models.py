from django.db import models
from django.utils.translation import gettext_lazy as _

from .managers import BookingManager, RoomAllocationManager

class Booking(models.Model):
    id = models.BigAutoField(primary_key=True, editable=False) 
    room = models.ForeignKey("rooms.Room", on_delete=models.SET_NULL, null=True)
    user = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True)
    check_in = models.DateTimeField(null=True)
    check_out = models.DateTimeField(null=True)
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)
    date_created = models.DateTimeField(auto_now_add=True, null = True)

    objects = BookingManager()


# Create your models here.
class RoomAllocation(models.Model):
    id = models.BigAutoField(primary_key=True, editable=False) 
    room = models.ForeignKey("rooms.Room", on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True, blank=True)
    status = models.IntegerField(null=True, blank=True)
    booking = models.ForeignKey(Booking, on_delete=models.SET_NULL, null=True, blank=True)
    availability_status = models.BooleanField(null=False, default=True)
    
    objects = RoomAllocationManager()
    

def __str__(self):
    return f"{self.id} -- {'Available' if self.availability_status else 'Unavailable'}"

# Create your models here.
class RoomStatusChange(models.Model):
    id = models.BigAutoField(primary_key=True, editable=False) 
    room = models.ForeignKey("rooms.Room", on_delete=models.SET_NULL, null=True, blank=True)
    reason = models.CharField(max_length=300, verbose_name=_("Reason for Status"))
    created_by = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    
    objects = RoomAllocationManager()