from django.core.exceptions import ValidationError
from rest_framework.exceptions import AuthenticationFailed, ValidationError, ValidationError
from django.core.validators import validate_email
from django.utils.translation import gettext_lazy as _
from django.db import models
from django.apps import apps
from datetime import datetime
from django.db.models import Q
from rest_framework import serializers
from .enums import RatingTag
from .utils import format_rating_records

class RatingManager(models.Manager):
    def create_rating(self, rating_type, description):
        Rating = apps.get_model('common.Rating')
        
        rating_type = int(rating_type)
        
        try:
            RatingTag(rating_type)  # Attempt to create an enum member from the value
            
            rating_Id = RatingTag[RatingTag(rating_type).name].value
            rating = Rating(rating_type=rating_Id, description=description)
            rating.save(using=self._db)
        
            return rating
          
        except ValueError:
            raise ValidationError(_("Rating type value is invalid"))
        
        # if rating_type not in RatingTag:
        #     raise ValidationError(_("Rating type value is invalid"))
        
        # try:
        #     rating_Id = RatingTag[RatingTag(rating_type).name].value
        #     rating = Rating(rating_type=rating_Id, description=description)
        #     rating.save(using=self._db)
            
        #     return rating
            
        # except Exception as e:
        #     raise serializers.ValidationError("An error occured, try again")
        

    def get_ratings(self, rating_type):
        Rating = apps.get_model('common.Rating')
        
        # If no rating type was passed to request, proceed to fetch all ratings regardless of type.
        if rating_type is None:
            records = Rating.objects.all()
            if len(records) < 1:
                raise ValidationError("No records were found")
            
            formatted_records = format_rating_records(records)
            return formatted_records
        
        rating_type = int(rating_type)
        if rating_type not in RatingTag:
            raise ValidationError(_("Rating type value is invalid"))
        
        try:
            if rating_type == RatingTag.WORSE.value:
                rating_type = RatingTag.WORSE.value
            
            elif rating_type == RatingTag.BAD.value:
                rating_type = RatingTag.BAD.value
                
            elif rating_type == RatingTag.GOOD.value:
                rating_type = RatingTag.GOOD.value
                
            elif rating_type == RatingTag.GREAT.value:
                rating_type = RatingTag.GREAT.value
                
            elif rating_type == RatingTag.EXCELLENT.value:
                rating_type = RatingTag.EXCELLENT.value
            
            rating_Id = RatingTag[RatingTag(rating_type).name].value
            records = Rating.objects.filter(**{'rating_type': rating_Id})
            if not records:
                raise ValidationError("No records were found")
            
            #formatted_records = format_rating_records(records)
            formatted_records = format_rating_records(records)
            return formatted_records
        
    
        except Exception as e:
            raise ValidationError(e.detail)