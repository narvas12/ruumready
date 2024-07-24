from django.core.exceptions import ValidationError
from rest_framework.exceptions import AuthenticationFailed, ValidationError, NotFound
from django.core.validators import validate_email
from django.utils.translation import gettext_lazy as _
from django.db import models
from django.apps import apps
from datetime import datetime, date
from django.db.models import Q
from rest_framework import serializers
from .utils import format_room_allocation_records, is_between
from utils.methods import cast_to_int_with_errors
from django.db.models import Q
from django.db.models import Sum, Count


from .enums import RoomStatus

class BookingManager(models.Manager):
    
    
    # ===============================modified create_booking manager to allow user book a room multiple times except overlapong dates=====================
    def create_booking(self, room_id, user_id, start_date, end_date):
        Room = apps.get_model('rooms', 'Room')
        UserModel = apps.get_model('accounts', 'User')
        RoomAllocationModel = apps.get_model('reservations', 'RoomAllocation')
        Booking = apps.get_model('reservations', 'Booking')

        BOOKED_STATUS = RoomStatus.BOOKED.value

        if not room_id:
            raise serializers.ValidationError(_("Room Id is required"))
        if not user_id:
            raise serializers.ValidationError(_("User Id is required"))
        if not start_date:
            raise serializers.ValidationError(_("Start date is required"))
        if not end_date:
            raise serializers.ValidationError(_("End date is required"))

        # Fetch room allocation instance
        room_allocation_instance = RoomAllocationModel.objects.filter(room_id=room_id).first()
        if not room_allocation_instance:
            raise NotFound("Room does not exist")

        if not room_allocation_instance.availability_status:
            raise serializers.ValidationError(_("Room is currently unavailable"))

        # Check room availability by dates
        self.check_room_availability_by_dates(room_id, start_date, end_date)

        # Fetch room instance
        room_instance = Room.objects.filter(id=room_id).first()
        if not room_instance:
            raise NotFound("Room does not exist")

        # Fetch user instance
        user_instance = UserModel.objects.filter(guest_id=user_id).first()
        if not user_instance:
            raise NotFound("User does not exist")
        
        if user_instance.is_staff:
            raise serializers.ValidationError("Not accessible to Administrator")

        # Check if the user has already booked the room for non-overlapping dates
        existing_bookings = Booking.objects.filter(
            room=room_instance,
            user=user_instance,
            end_date__gte=start_date,
            start_date__lte=end_date
        )
        if existing_bookings.exists():
            raise serializers.ValidationError(_("User has already booked the room for other dates"))

        # Proceed with booking if everything is valid
        booking = self.model(room=room_instance, user=user_instance, start_date=start_date, end_date=end_date)
        booking.save(using=self._db)

        try:
            room_allocation_instance.room = room_instance
            room_allocation_instance.status = BOOKED_STATUS
            room_allocation_instance.booking = booking

            booking.save(using=self._db)
            room_allocation_instance.save(using=self._db)

        except Exception as e:
            return e

        return booking
    
    
    # =========================================modified create_boopking_1==================================
    def create_booking_1(self, room_id, user_id, start_date, end_date):
        # access respective models with django apps to avoid circular dependency
        Room = apps.get_model('rooms', 'Room')
        UserModel = apps.get_model('accounts', 'User')
        RoomAllocationModel = apps.get_model('reservations', 'RoomAllocation')
        Booking = apps.get_model('reservations', 'Booking')
        
        BOOKED_STATUS = RoomStatus.BOOKED.value
        
        if not room_id:
            raise serializers.ValidationError(_("Room Id is required"))
        if not user_id:
            raise serializers.ValidationError(_("User Id is required"))
        if not start_date:
            raise serializers.ValidationError(_("Start date is required"))
        if not end_date:
            raise serializers.ValidationError(_("End date is required"))
        
        room_allocation_instance = RoomAllocationModel.objects.filter(**{'room': room_id})
        if not room_allocation_instance:
            raise NotFound("Room does not exist")
        room_allocation_instance = room_allocation_instance[0]
        
        if not room_allocation_instance.availability_status:  
            raise serializers.ValidationError(_("Room is currently unavailable"))
        
        should_proceed_with_booking = self.check_room_availability_by_dates(room_id, start_date, end_date)
        
        room_instance = Room.objects.filter(**{'id': room_id})
        if not room_instance:
            raise NotFound("Room does not exist")
        room_instance = room_instance[0]
        
        user_instance = UserModel.objects.filter(**{'guest_id': user_id})
        if not user_instance:
            raise NotFound("User does not exist")
        user_instance = user_instance[0]
        
        if user_instance.is_staff:
            raise serializers.ValidationError("Not accessible to Administrator")
        
        # Check if the user has already booked the room for non-overlapping dates
        existing_bookings = Booking.objects.filter(
            room=room_instance,
            user=user_instance,
            end_date__gte=start_date,
            start_date__lte=end_date
        )
        if existing_bookings.exists():
            raise serializers.ValidationError(_("User has already booked the room for other dates"))
        
        # Proceed with booking if everything is valid
        booking = self.model(room=room_instance, user=user_instance, start_date=start_date, end_date=end_date)
        booking.save(using=self._db)
        
        try:
            room_allocation_instance.room = room_instance
            room_allocation_instance.status = BOOKED_STATUS
            room_allocation_instance.booking = booking
            
            booking.save(using=self._db)
            room_allocation_instance.save(using=self._db)
            
        except Exception as e:
            return e
        
        return booking
        
  
    def check_room_availability_by_dates(self, room_id, start_date, end_date):
        Booking = apps.get_model('reservations', 'Booking')
        today = date.today()

        if start_date < today:
            raise serializers.ValidationError(_("Start date cannot be in the past"))
        if end_date <= today:
            raise serializers.ValidationError(_("End date cannot be in the past"))
        if start_date == end_date:
            raise serializers.ValidationError(_("End date cannot be the same as start date"))

        overlapping_bookings = Booking.objects.filter(
            room_id=room_id,
            start_date__lt=end_date,
            end_date__gt=start_date
        )

        if overlapping_bookings.exists():
            raise serializers.ValidationError(_("Room is already booked for this period"))

        return True
    
    
    def check_user_in(self, user_id, room_id):
        Booking = apps.get_model('reservations', 'Booking')
        UserModel = apps.get_model('accounts', 'User')
        RoomAllocationModel = apps.get_model('reservations', 'RoomAllocation')
        
        CHECKED_IN_STATUS = RoomStatus.CHECKED_IN.value
        
        if not user_id:
            raise serializers.ValidationError(_("User ID is required"))
        
        user_instance = UserModel.objects.filter(**{'guest_id': user_id})
        if not user_instance:
            raise serializers.ValidationError("User does not exist")
        user_instance = user_instance[0]
        
        if user_instance.is_staff:
          raise serializers.ValidationError("Not accessible to Administrator")
    
        
        booking_instance = Booking.objects.filter(Q(room_id = room_id) & Q(user_id = user_instance.id)).order_by('-date_created')
        if not booking_instance:
            raise serializers.ValidationError("User must book a room before check-in")
        booking_instance = booking_instance[0]
        if booking_instance.user.guest_id != user_id:  
            raise serializers.ValidationError(_("You have to book a room before you check-in"))
        if booking_instance.check_in is not None:  
            raise serializers.ValidationError(_("User has already checked-in"))

        room_allocation_instance = RoomAllocationModel.objects.filter(Q(room_id = room_id))[0]
        
        if not room_allocation_instance.availability_status:  
            raise serializers.ValidationError(_("Room is currently unavailable"))
        
        status_Id = RoomStatus[RoomStatus(CHECKED_IN_STATUS).name].value
        
        # GET THE BOOKING RECORD AND UPDATE THE USER CHECK IN TIME
        check_in_time = datetime.now()
        booking_instance.check_in = check_in_time
        booking_instance.save(using=self._db)
    
        # GET THE ROOM ALLOCATION RECORD AND UPDATE THE ROOM STATUS TO CHECKED IN
        room_allocation_instance.status = status_Id
        room_allocation_instance.booking = booking_instance
        room_allocation_instance.user = user_instance
        room_allocation_instance.save(using=self._db)
        
        return room_allocation_instance 
    
    
    
    
    
    def check_user_out(self, user_id, room_id):
        Booking = apps.get_model('reservations', 'Booking')
        UserModel = apps.get_model('accounts', 'User')
        RoomAllocationModel = apps.get_model('reservations', 'RoomAllocation')
        
        CHECKED_OUT_STATUS = RoomStatus.CHECKED_OUT.value
        AVAILABLE_STATUS = RoomStatus.AVAILABLE.value
        BOOKED_STATUS = RoomStatus.BOOKED.value
        
        if not user_id:
            raise serializers.ValidationError(_("User ID is required"))
        
        user_instance = UserModel.objects.filter(**{'guest_id': user_id}).first()
        if not user_instance:
            raise serializers.ValidationError("User does not exist")
        
        if user_instance.is_staff:
            raise serializers.ValidationError("Not accessible to Administrator")
        
        booking_instance = Booking.objects.filter(Q(room_id=room_id) & Q(user_id=user_instance.id)).order_by('-date_created').first()
        if not booking_instance:
            raise serializers.ValidationError("User must book a room before check-out")
        
        if booking_instance.check_out is not None:
            raise serializers.ValidationError(_("User has already checked-out"))
        
        room_allocation_instance = RoomAllocationModel.objects.filter(Q(room_id=room_id)).first()
        if not room_allocation_instance:
            raise serializers.ValidationError(_("Room allocation does not exist"))
        
        if room_allocation_instance.status in [CHECKED_OUT_STATUS, AVAILABLE_STATUS, BOOKED_STATUS]:
            raise serializers.ValidationError(_("User must be checked-in before checkout"))
        
        status_Id = RoomStatus[RoomStatus(AVAILABLE_STATUS).name].value

        # GET THE BOOKING RECORD AND UPDATE THE USER CHECK OUT TIME
        check_out_time = datetime.now()
        booking_instance.check_out = check_out_time

        # GET THE ROOM ALLOCATION RECORD AND UPDATE THE ROOM STATUS TO CHECKED OUT
        room_allocation_instance.status = status_Id
        room_allocation_instance.user = None
        room_allocation_instance.booking = None
        
        booking_instance.save(using=self._db)
        room_allocation_instance.save(using=self._db)
        
        return room_allocation_instance
    
    def check_user_out_ext(self, id_list):
        Booking = apps.get_model('reservations', 'Booking')
        UserModel = apps.get_model('accounts', 'User')
        RoomAllocation = apps.get_model('reservations', 'RoomAllocation')
        
        CHECKED_OUT_STATUS = RoomStatus.CHECKED_OUT.value
        AVAILABLE_STATUS = RoomStatus.AVAILABLE.value
        BOOKED_STATUS = RoomStatus.BOOKED.value
        
        for id in id_list:
            status_Id = RoomStatus[RoomStatus(AVAILABLE_STATUS).name].value
            record = RoomAllocation.objects.filter(**{'id': id})
            if not record:
                raise serializers.ValidationError("Record does not exist")
            record = record[0]
            
            # GET THE BOOKING RECORD AND UPDATE THE USER CHECK OUT TIME
            booking_record = Booking.objects.filter(**{'id': record.booking.id})
            if not booking_record:
                raise serializers.ValidationError("Record does not exist")
            booking_record = booking_record[0]
            
            check_out_time = datetime.now()
            booking_record.check_out = check_out_time
        
            # GET THE ROOM ALLOCATION RECORD AND UPDATE THE ROOM STATUS TO CHECKED OUT
            record.status = status_Id
            record.user = None
            record.booking = None
            
            booking_record.save(using=self._db)
            record.save(using=self._db)
            
        return record
            
    def get_bookings_history(self):
        #Assigning Models
        Booking = apps.get_model('reservations', 'Booking')
        
        records = Booking.objects.all().order_by("-date_created")
        if not records:
            raise serializers.ValidationError("No records were found")
        
        return records
    
    
    
    def get_rooms_overview(self):
        #Assigning Models
        Booking = apps.get_model('reservations', 'Booking')
        #RoomAllocation = apps.get_model('reservations', 'RoomAllocation')
        
        # Filter objects where "created_at" field's date is equal to today
        records = Booking.objects.all().order_by("-date_created")
        if not records:
            serializers.ValidationError("No records found for that period")
        return records
        
       
    
    def get_rooms_overview_for_doc(self, date_from, date_to):
        #Assigning Models
        Booking = apps.get_model('reservations', 'Booking')
        #RoomAllocation = apps.get_model('reservations', 'RoomAllocation')
        
        if date_from and date_to:
            records = Booking.objects.filter(date_created__gte=date_from,date_created__lte=date_to)
            if not records:
                raise serializers.ValidationError("No records found for that period")
            return records
        
        elif date_from and (date_to == None or date_to == ""):
            records = Booking.objects.filter(date_created__gte=date_from)
            if not records:
                raise serializers.ValidationError("No records found for that period")
            return records
        
        # elif date_from > date_to:
        #     raise serializers.ValidationError("Start date cannot be greater that end date")
        
        elif date_from is None and (date_to is not None or date_to == ""):
            raise serializers.ValidationError("Date from is not set")

        
    def get_current_rooms_overview(self):
        #Assigning Models
        Booking = apps.get_model('reservations', 'Booking')
        #RoomAllocation = apps.get_model('reservations', 'RoomAllocation')
        
        today = date.today()

        # Filter objects where "created_at" field's date is equal to today
        records_today = Booking.objects.filter(date_created__date=today).order_by("-date_created")
        if not records_today:
            return []
        return records_today
    
    def get_user_rooms_overview(self, user_id):
        #Assigning Models
        Booking = apps.get_model('reservations', 'Booking')
       
        records = Booking.objects.filter(**{'user':user_id}).order_by("-date_created")
        if not records:
            return []
        
        return records
    
    
    
    
    def get_user_booked_rooms(self, user_id):
        RoomAllocation = apps.get_model('reservations', 'RoomAllocation')
        Booking = apps.get_model('reservations', 'Booking')
        
        if not user_id:
            raise serializers.ValidationError("User ID is required")

        user_instance = apps.get_model('accounts', 'User')
        if not user_instance:
            raise serializers.ValidationError("User does not exist")

        bookings = Booking.objects.filter(user=user_id, check_in__isnull=True)

        booked_rooms = []
        for booking in bookings:
            room_allocations = RoomAllocation.objects.filter(
                booking=booking
            )

            for allocation in room_allocations:
                room_details = {
                    'room_id': allocation.room.id,
                    'room': allocation.room.room_name,
                    'start_date': booking.start_date,
                    'end_date': booking.end_date,
                    'check_in': booking.check_in,
                    'check_out': booking.check_out,
                }
                booked_rooms.append(room_details)

        return booked_rooms


class RoomAllocationManager(models.Manager):
    
    def get_rooms(self, room_status):
        #Assigning Models
        RoomAllocation = apps.get_model('reservations', 'RoomAllocation')
        
        # If no status was passed to request, proceed to fetch all rooms regardless of status.
        if room_status is None:
            records = RoomAllocation.objects.all()
            if len(records) < 1:
                raise serializers.ValidationError("No records were found")
            
            formatted_records = format_room_allocation_records(records)
            return formatted_records
        
        room_status = int(room_status)
        check_parsed_status = cast_to_int_with_errors(room_status)
        if not check_parsed_status:
            raise serializers.ValidationError(_("Status value is invalid"))
        room_status = int(room_status)
        if not RoomStatus.enum_has_value(int(room_status)):
            raise serializers.ValidationError(_("Status value is invalid"))
        
        status_param = None
        
        if room_status == RoomStatus.AVAILABLE.value:
            status_param = RoomStatus.AVAILABLE.value
        
        elif room_status == RoomStatus.UNAVAILABLE.value:
            status_param = RoomStatus.UNAVAILABLE.value
            
        elif room_status == RoomStatus.BOOKED.value:
            status_param = RoomStatus.BOOKED.value
            
        elif room_status == RoomStatus.CHECKED_IN.value:
            status_param = RoomStatus.CHECKED_IN.value
            
        elif room_status == RoomStatus.CHECKED_OUT.value:
            status_param = RoomStatus.CHECKED_OUT.value
        
        status_Id = RoomStatus[RoomStatus(status_param).name].value
        records = RoomAllocation.objects.filter(**{'status': status_Id})
        if not records:
            raise serializers.ValidationError("No records were found")
        
        formatted_records = format_room_allocation_records(records)
        return formatted_records
    
    def get_rooms_for_checkout(self, param):
        #Assigning Models
        RoomAllocation = apps.get_model('reservations', 'RoomAllocation')
        User = apps.get_model('accounts', 'User')
        
        if not param:
            raise serializers.ValidationError("Search parameter not supplied")
        
        user_record = User.objects.filter(Q(mobile__icontains=param) | Q(guest_id__icontains=param))
        if not user_record:
            raise serializers.ValidationError("User does not exist")
        user_record=user_record[0]
        
        if user_record.is_staff:
            raise serializers.ValidationError("Not accessible to Administrator")
        
        records = RoomAllocation.objects.filter(**{'user': user_record.id})
        if not records:
            raise serializers.ValidationError("You are not checked into any room")
        
        return records
    


    def get_dashboard_bootstrap_data(self):
        # Assigning Models
        Rooms = apps.get_model('rooms', 'Room')
        Booking = apps.get_model('reservations', 'Booking')
        Ratings = apps.get_model('common', 'Rating')
        User = apps.get_model('accounts', 'User')
        
        record = {}
        guest_count = 0
        room_count = 0        
        checkin_count = 0        
        checkout_count = 0        
        rating_average = 0 
        average_checkins_per_day = 0
        
        CHECKED_IN_STATUS = RoomStatus.CHECKED_IN.value
        status_Id = RoomStatus[RoomStatus(CHECKED_IN_STATUS).name].value
        
        
        guest_count = User.objects.filter(is_staff=False).count()
            

        room_count = Rooms.objects.count()
            

        checkin_count = Booking.objects.exclude(check_in=None).count()
        checkout_count = Booking.objects.exclude(check_out=None).count()
        

        # total_checkins = Booking.objects.exclude(check_in=None).count()
        distinct_dates = Booking.objects.exclude(check_in=None).values('check_in__date').annotate(count=Count('check_in__date'))
        total_days = len(distinct_dates)
        average_checkins_per_day = checkin_count / total_days if total_days > 0 else 0
        

        ratings_record = Ratings.objects.all()
        if ratings_record.exists():
            rating_sum = ratings_record.aggregate(Sum('rating_type'))['rating_type__sum']
            rating_count = ratings_record.count()
            rating_average = rating_sum / rating_count if rating_count > 0 else 0
        
        record["guest_count"] = guest_count
        record["checkin_count"] = checkin_count
        record["average_checkins_per_day"] = average_checkins_per_day
        record["checkout_count"] = checkout_count
        record["room_count"] = room_count
        record["rating_average"] = rating_average
        
        
        return record
    
    
    def get_room_bootstrap_data(self):
        #Assigning Models
        RoomAllocation = apps.get_model('reservations', 'RoomAllocation')
        Booking = apps.get_model('reservations', 'Booking')
     
        record = {}
        room_count = 0        
        available_rooms = []
        unavailable_rooms = []
        booked_rooms = []
            
        AVAILABLE_STATUS = RoomStatus.AVAILABLE.value
        UNAVAILABLE_STATUS = RoomStatus.UNAVAILABLE.value
        BOOKED_STATUS = RoomStatus.BOOKED.value
        CHECKEDIN_STATUS = RoomStatus.CHECKED_IN.value

        #Settin Room count
        room_records = RoomAllocation.objects.all()
        if len(room_records) < 1:
            room_count = 0
        elif len(room_records) > 0:
            room_count = len(room_records)
            
        #Settin available_rooms
        available_records = RoomAllocation.objects.filter(**{'status': AVAILABLE_STATUS})
        if len(available_records) < 1:
            available_rooms = []
        elif len(available_records) > 0:
            for r in available_records:
                room_id = r.room.room_id
                available_rooms.append(room_id)
                
    
        #Settin unavailable_rooms
        unavailable_records = RoomAllocation.objects.filter(**{'status': UNAVAILABLE_STATUS })
        checkedin_records = RoomAllocation.objects.filter(**{'status': CHECKEDIN_STATUS })
        
        if len(unavailable_records) < 1:
            unavailable_rooms = []
        elif len(unavailable_records) > 0:
            for r in unavailable_records:
                room_id = r.room.room_id
                unavailable_rooms.append(room_id)
                
        if len(checkedin_records) < 1:
            pass
        elif len(checkedin_records) > 0:
            for r in checkedin_records:
                room_id = r.room.room_id
                unavailable_rooms.append(room_id)
        
        #Settin unavailable_rooms
        booked_records = RoomAllocation.objects.filter(**{'status': BOOKED_STATUS})
        if len(booked_records) < 1:
            booked_rooms = []
        elif len(booked_records) > 0:
            for r in booked_records:
                room_id = r.room.room_id
                booked_rooms.append(room_id)
                
        record["room_count"] = room_count
        record["available_rooms"] = available_rooms
        record["unavailable_rooms"] = unavailable_rooms
        record["booked_rooms"] = booked_rooms
        
        return record


    
    def get_room_history(self, room_id):
        Room = apps.get_model('rooms', 'Room')
        Booking = apps.get_model('reservations', 'Booking')
        RoomStatusChange = apps.get_model('reservations', 'RoomStatusChange')

        room = Room.objects.get(id=room_id)
        room_details = {
            "room_id": room.room_id,
            "room_name": room.room_name,
            "apartment_type": room.apartment_type.apartment_type if room.apartment_type else None,
        }

        booking_history = []
        status_changes = []

        # Get all bookings for the room and order by check-in date
        bookings = Booking.objects.filter(room=room).order_by('check_in')
        for booking in bookings:
            booking_info = {
                "check_in": booking.check_in,
                "check_out": booking.check_out,
                "user_guest_id": booking.user.guest_id if booking.user else None,
                "user_full_name": booking.user.full_name if booking.user else None,
                "user_mobile": booking.user.mobile if booking.user else None,
                "user_email": booking.user.email if booking.user else None,
            }
            booking_history.append(booking_info)

        # Get all status changes for the room and order by date created
        room_status_changes = RoomStatusChange.objects.filter(room=room).order_by('date_created')
        for status_change in room_status_changes:
            status_change_info = {
                "reason": status_change.reason,
                "created_by": status_change.created_by.email if status_change.created_by else None,
                "date_created": status_change.date_created,
            }
            status_changes.append(status_change_info)

        return {
            "room_details": room_details,
            "booking_history": booking_history,
            "status_changes": status_changes,
        }