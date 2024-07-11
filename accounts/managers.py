from django.contrib.auth.models import BaseUserManager
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import validate_email
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from common.notification import Notification 
import asyncio
from django.apps import apps
from rest_framework.exceptions import NotFound, ValidationError
import requests
from django.db import models

from .utils.api import get_verified_userdetails_by_phone  as _get_verified_userdetails_by_phone
from rest_framework import serializers
import cloudinary
from django.db.models import Q


cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET
)

class UserManager(BaseUserManager):
    def upload_image(self, file):
        image_file = file
       # upload_result = cloudinary.uploader.upload(image_file, public_id='custom_id')  # Optional public_id
        upload_result = cloudinary.uploader.upload(image_file)  # Optional public_id

        if upload_result['secure_url']:
            # Image uploaded successfully, store url in database or use directly
            return upload_result['secure_url']
        else:
            # Handle upload error
            return "error"
            #return upload_result['error']['message']
    
    def email_validator(self, email):
        try:
            validate_email(email)
        except ValidationError:
            raise ValidationError(_("please enter a valid email address"))
        
    def create_walkin_user(self, mobile, full_name, password, guest_id, email, room_id, start_date, end_date, doc = None, **extra_fields):
        Booking = apps.get_model('reservations', 'Booking')
        Room = apps.get_model('rooms', 'Room')
        User = apps.get_model('accounts', 'User')
        
        
        should_proceed_with_booking = Booking.objects.check_room_availability_by_dates(room_id, start_date, end_date)
        
        try:
            room = Room.objects.get(id=room_id)
        
        except Room.DoesNotExist:
             raise NotFound("Room does not exist")
         
        
        
        user = self.model(mobile=mobile, full_name=full_name, guest_id=guest_id, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        
        # Send email and sms to new user
        html_content = f"Welcome to Luxeville Hotels. Your Guest ID is: {guest_id}"
        email_subject = "Welcome!"
        sms_msg = html_content
        
        
        # SEND NOTIFICATIONS HERE
        Notification.send_email_async(to_email=email, subject=email_subject, html_content=html_content)
        Notification.send_sms_async(recipient=mobile, message=sms_msg)
        
        try:
            # uploading image then set the sgring in the db
            if doc:
                file = doc
                secure_url = self.upload_image(file)  
                
                user.valid_id = str(secure_url)
                user.save(using=self._db)
                
            Booking.objects.create_booking(
                room_id = room_id,
                user_id = user.guest_id,
                start_date = start_date,
                end_date = end_date,
            )
            
        except Exception as e:
              user = User.objects.get(guest_id=guest_id)
              if User.DoesNotExist():
                  pass
              user.delete()
              raise serializers.ValidationError("Something happened while creating your account")
        
        return user

    def create_walkin_userInit(self, mobile, full_name, password, guest_id, email,  **extra_fields):

        user = self.model(mobile=mobile, full_name=full_name, guest_id=guest_id, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        
        # Send email and sms to new user
        html_content = f"Welcome to Luxeville Hotels. Your Guest ID is: {guest_id}"
        email_subject = "Welcome!"
        sms_msg = html_content
        
        Notification.send_email_async(to_email=email, subject=email_subject, html_content=html_content)
        Notification.send_sms_async(recipient=mobile, message=sms_msg)
         
        return user

    def create_user(self, email, full_name, password, guest_id, **extra_fields):
        if email:
            email = self.normalize_email(email)
            self.email_validator(email)
        else:
            raise ValidationError(_("Base User Account: An email address is required"))
        if not full_name:
            raise ValidationError(_("Fullname is required"))
        user = self.model(email=email, full_name=full_name, **extra_fields)
        user.guest_id = guest_id
        user.set_password(password)
        user.save(using=self._db)
        
      
        
        return user

    def create_adminuser(self, email, full_name, password, **extra_fields):
            #GUEST_ID_FOR_STAFF = str(settings.GUEST_ID_FOR_STAFF)
            GUEST_ID_FOR_STAFF = None
        
            extra_fields.setdefault("is_staff", True)
            extra_fields.setdefault("is_verified", True)

            if extra_fields.get("is_staff") is not True:
                raise ValidationError(_("is staff must be true for admin user"))

            user = self.create_user(
                email, full_name, password, GUEST_ID_FOR_STAFF,  **extra_fields
            )
            user.save(using=self._db)
            return user

    def create_superuser(self, email, full_name, password, **extra_fields):
        GUEST_ID_FOR_STAFF = None
        
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_verified", True)

        if extra_fields.get("is_staff") is not True:
            raise ValidationError(_("is staff must be true for admin user"))

        if extra_fields.get("is_superuser") is not True:
            raise ValidationError(_("is superuser must be true for admin user"))

        user = self.create_user(
            email, full_name, password, GUEST_ID_FOR_STAFF, **extra_fields
        )
        user.save(using=self._db)
        return user


    def get_user(self, param=None ):
        User = apps.get_model('accounts.User')
    
        if not param:
            raise serializers.ValidationError("Search param not supplied")
        
        user_record = User.objects.filter(Q(mobile__icontains=param) | Q(guest_id__icontains=param) | Q(email__icontains=param))
        if not user_record:
            raise serializers.ValidationError("User does not exist")
        user_record=user_record[0]
        
        return user_record
    
    
           
    
    def get_user_by_phone(self, mobile):
        User = apps.get_model('accounts.User')
     
        record = User.objects.filter(**{'mobile': mobile})
        if not record:
            raise NotFound("User does not exist")
        record = record[0]
        return record
    
      
    def get_verified_user_details(self, user_id):
        MobileVerification = apps.get_model('accounts.MobileVerification')
        User = apps.get_model('accounts.User')
     
        user_record = User.objects.filter(**{'id': user_id})
        if not user_record:
            raise NotFound("User does not exist")
     
        record = MobileVerification.objects.filter(**{'user': user_id})
        if not record:
            raise NotFound("User has not been verified")
        record = record[0]
        return record
    
    def get_all_users(self):
        User = apps.get_model('accounts.User')
        
        records = User.objects.filter(**{"is_staff": False}).order_by("-date_created")
        if len(records) < 1:
            raise NotFound("No records were found")
        return records
    

class VerificationManager(models.Manager):
    
    def get_verified_userdetails_by_phone(self, phone_number):
        MobileVerification = apps.get_model('accounts.MobileVerification')
        User = apps.get_model('accounts.User')

        if phone_number is None:
            raise ValidationError(_("Phone number is required"))
        
        try:
            # fetch user instance
            user_instance = User.objects.filter(**{'mobile': phone_number})
            if not user_instance:
                    raise NotFound("User does not exist")
            user_instance = user_instance[0]
            
            #Check the verifications table if number has not beeen verified in the past
            verified_user_instance = MobileVerification.objects.filter(**{'msisdn': phone_number})
            if verified_user_instance:
                return verified_user_instance[0]
            
            verified_details = _get_verified_userdetails_by_phone(phone_number=phone_number)
            if  verified_details is None:
                raise ValidationError("Verification Not Sucessful")
            
            #change user status to verified
            if not user_instance.is_mobile_verified:
                user_instance.is_mobile_verified = True
            
            verified_user = MobileVerification(msisdn=verified_details.get("msisdn"), 
                                                    first_name=verified_details.get("firstName"), 
                                                    middle_name=verified_details.get("MiddleName"), 
                                                    last_name=verified_details.get("lastName"), 
                                                    user=user_instance, 
                                                    email=verified_details.get("email", ), 
                                                    date_of_birth=verified_details.get("dateOfBirth"),
                                                    gender=verified_details.get("gender"),
                                                    address=verified_details.get("address"),
                                                    address_city=verified_details.get("addressCity"),
                                                    address_state=verified_details.get("addressState"),
                                                )
            user_instance.save(using=self._db)
            verified_user.save(using=self._db)
            
            return verified_user
            
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
       