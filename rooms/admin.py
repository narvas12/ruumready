from django.contrib import admin

from .models import Room, ApartmentType

# Register your models here.
admin.site.register(Room)
admin.site.register(ApartmentType)