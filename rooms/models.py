from django.db import models
from django.utils.translation import gettext_lazy as _
from rest_framework_simplejwt.tokens import RefreshToken

from .managers import RoomManager, ApartmentManager

# Create your models here.
class ApartmentType(models.Model):
    id = models.BigAutoField(primary_key=True, editable=False) 
    apartment_type = models.CharField(max_length=50, verbose_name=_("Apartment Type"), null=True, unique=True)
    description = models.CharField(max_length=255, verbose_name=_("Description"), null=True)
    
   
    
    REQUIRED_FIELDS = ["apartment_type"]
    
    objects = ApartmentManager()

def __str__(self):
    return self.apartment_type 

class Room(models.Model):
    id = models.BigAutoField(primary_key=True, editable=False) 
    room_id = models.CharField(max_length=10, verbose_name=_("Room Id"), null=True, unique=True)
    room_name = models.CharField(max_length=50, verbose_name=_("Room Name"), null=True, unique=True)
    description = models.CharField(max_length=255, verbose_name=_("Room Description"), null=True)
    apartment_type = models.ForeignKey(ApartmentType, on_delete=models.SET_NULL, null=True)
    amount_daily = models.DecimalField(verbose_name=_("Amount Per Day"), max_digits=12, decimal_places=2, null=True)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True, null = True)
 

    REQUIRED_FIELDS = ["room_id", "room_name", "apartment_type", "description"]

    objects = RoomManager()

    def __str__(self):
        return self.room_name
    
