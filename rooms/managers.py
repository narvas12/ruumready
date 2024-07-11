from django.contrib.auth.models import BaseUserManager
from django.core.exceptions import ValidationError
from rest_framework.exceptions import AuthenticationFailed, ValidationError,NotFound
from django.core.validators import validate_email
from django.utils.translation import gettext_lazy as _
from django.db import models
from django.apps import apps
from asgiref.sync import sync_to_async
from rest_framework import serializers
from reservations.enums import RoomStatus
from django.db.models import Q


class RoomManager(models.Manager):
    
    def create_room(self, room_id, room_name, apartment_type, **extra_fields):
        try:
            # access respective models with django apps to avoid circular dependency
            Room = apps.get_model('rooms.Room')
            RoomAllocation = apps.get_model('reservations.RoomAllocation')
            
            AVAILABLE_STATUS = RoomStatus.AVAILABLE.value 
            
            extra_fields.setdefault("is_active", True)
        
            if not room_id:
                raise ValidationError(_("Room Id is required"))
            if not room_name:
                raise ValidationError(_("Room Name is required"))

            room = self.model(room_id=room_id, room_name=room_name, apartment_type=apartment_type, **extra_fields)
            room.save(using=self._db)
            
            
            # ADD ROOM INFORMATION TO ROOM ALLOCATION TABLE
            room_instance = Room.objects.filter(**{'room_id': room_id})[0]
            room_allocation_instance = RoomAllocation.objects.filter(room_id=room_instance.id).exists()
        
            if not room_allocation_instance:
                status_Id = RoomStatus[RoomStatus(AVAILABLE_STATUS).name].value
                room_allocation = RoomAllocation(
                    room = room_instance,
                    user = None,
                    status = status_Id,
                    booking = None,
                )
                
                room_allocation.save(using=self._db)
            
            return room
        except Exception as e:
            return e
    
    def get_room(self, room_id):
        Room = apps.get_model('rooms.Room')
        
        try:
            record = Room.objects.get(id=room_id)
            return record
        
        except self.model.DoesNotExist:
            raise NotFound("Room does not exist")
        
    def get_all_rooms(self):
        Room = apps.get_model('rooms.Room')
        
        records = Room.objects.all().order_by("room_name")
        if len(records) < 1:
            raise NotFound("No records were found")
        return records
    
    def delete_room(self, room_id):
        Room = apps.get_model('rooms.Room')
        
        try:
            record = Room.objects.get(id=room_id)
            record.delete()
        
        except self.model.DoesNotExist:
             raise NotFound("Room does not exist")
         
    
    def update_room(self, instance, validated_data):
        # access respective models with django apps to avoid circular dependency
        Room = apps.get_model('rooms.Room')
        ApartmentType = apps.get_model('rooms.ApartmentType')
        
        room_id = validated_data.get('room_id', instance.room_id)
        room_name = validated_data.get('room_name', instance.room_name)
        description = validated_data.get('description', instance.description)
        amount_daily = validated_data.get('amount_daily', instance.amount_daily)
        
        apartment_type_id = validated_data.get('apartment_type').id
        apartment_type = ApartmentType.objects.get(id=apartment_type_id)
        
        #excluded_record_id = 'R309'  # Replace with the actual ID you want to exclude
        #all_rooms = Room.objects.exclude(Q(room_id=excluded_record_id) | Q(room_id=True))
        
        instance.room_id = room_id
        instance.room_name = room_name
        instance.apartment_type = apartment_type #apartment_type'),
        instance.description = description
        instance.amount_daily = amount_daily
        
        instance.save()
        return instance
        
    
class ApartmentManager(models.Manager):   
    def create_apartment_type(self, apartment_type, **extra_fields):
        if not apartment_type:
            raise ValidationError(_("Apartment type is required"))
       
        apartment_type = self.model(apartment_type=apartment_type,**extra_fields)
        apartment_type.save(using=self._db)
        
        return apartment_type
    
    
    def get_apartment_type(self, apartment_type_id):
        ApartmentType = apps.get_model('rooms.ApartmentType')
        
        try:
            record = ApartmentType.objects.get(id=apartment_type_id)
            return record
        
        except self.model.DoesNotExist:
            raise NotFound("Apartment type does not exist")
        
        
    def get_all_apartment_types(self):
        ApartmentType = apps.get_model('rooms.ApartmentType')
        
        records = ApartmentType.objects.all()
        if len(records) < 1:
            raise NotFound("No records were found")
        return records
    
    
    def delete_apartment_type(self, apartment_type_id):
        ApartmentType = apps.get_model('rooms.ApartmentType')
        
        try:
            record = ApartmentType.objects.get(id=apartment_type_id)
            record.delete()
        
        except self.model.DoesNotExist:
             raise NotFound("Apartment Type does not exist")
    