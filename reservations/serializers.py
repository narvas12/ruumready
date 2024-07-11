from .models import Booking, RoomAllocation, RoomStatusChange
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed, ValidationError, NotFound
from django.apps import apps
from django.utils.translation import gettext_lazy as _
from .validators import checkBool
from django.db.models import UUIDField
from .enums import RoomStatus

# access respective models with django apps to avoid circular dependency
RoomModel = apps.get_model('rooms.Room')
UserModel = apps.get_model('accounts.User')
BookingModel = apps.get_model('reservations.Booking')

class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model=RoomModel
        fields = ['id', 'room_id', 'room_name', 'description', 'amount_daily', 'apartment_type']
        
        depth = 2

class RoomAllocationSerializer(serializers.ModelSerializer):
    
    class Meta:
        model=RoomAllocation
        fields = ['room', 'user', 'booking']

        read_only_fields = ('room', 'user', 'booking')
        depth = 2
        
class UserSerializer(serializers.ModelSerializer):
    # id = serializers.UUIDField(format='hex')
    class Meta:
        model = UserModel
        fields = ['guest_id', 'email', 'mobile', 'full_name', 'valid_address',  'valid_id', 'occupation', 'date_joined']
        
class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookingModel
        fields = ['check_in', 'check_out', 'date_created']
        
class BookingsHistorySerializer(serializers.ModelSerializer):
    user = UserSerializer(many=False, read_only=True)
    room = RoomSerializer(many=False, read_only=True)
    class Meta:
        model = BookingModel
        fields = ['id', 'check_in', 'check_out', 'date_created', 'room', 'user', 'end_date', 'start_date']
        
    depth = 1
    

class RoomByStatusSerializer(serializers.ModelSerializer):
    user = UserSerializer(many=False, read_only=True)
    booking = BookingSerializer(many=False, read_only=True)
    room = RoomSerializer(many=False, read_only=True)
    status = serializers.CharField(max_length=12, min_length=4, read_only=True)
    
    class Meta:
        model=RoomAllocation
        fields = ['id', 'status', 'availability_status', 'room', 'user', 'booking']

        depth = 2
        
class CheckInSerializer(serializers.Serializer):
    user_id = serializers.CharField(max_length=100, min_length=4, write_only=True)
    
    class Meta:
        fields = '__all__'

    def validate(self, attrs):
        if not attrs.get('user'):
            pass
        
        return attrs

    def update(self, instance, validated_data):
        user_id = validated_data.get('user_id')
        room_id = validated_data.get('room_id')
        
        model = Booking.objects.check_user_in(
                user_id = user_id,
                room_id = room_id
            )
        return model


class MultipleCheckInSerializer(serializers.Serializer):
    user_id = serializers.CharField(max_length=100, min_length=4, write_only=True)
    room_ids = serializers.ListField(child=serializers.IntegerField(), write_only=True)  # Assuming room_ids will be a list of integers
    
    class Meta:
        fields = '__all__'  # This is not necessary in a Serializer class, as Meta is typically used in ModelSerializer

    def validate(self, attrs):
        user_id = attrs.get('user_id')
        room_ids = attrs.get('room_ids')
        
        if not user_id:
            raise serializers.ValidationError("User ID is required")
        
        if not room_ids:
            raise serializers.ValidationError("Room IDs are required")
        
        # Validate room_ids further if needed (e.g., check if they are valid room IDs)
        # Add your validation logic here
        
        return attrs

    def update(self, instance, validated_data):
        user_id = validated_data.get('user_id')
        room_ids = validated_data.get('room_ids')
        
        # Perform the check-in operation for each room ID
        for room_id in room_ids:
            model = Booking.objects.check_user_in(user_id=user_id, room_id=room_id)
            # Optionally handle the model instance or return it
        
        return validated_data 
    
class CheckOutSerializer(serializers.Serializer):
    user_id = serializers.CharField(max_length=100, min_length=4, write_only=True)
    
    class Meta:
        fields = '__all__'

    def validate(self, attrs):
        if not attrs.get('user'):
            pass
        
        return attrs

    def update(self, instance, validated_data):
        user_id = validated_data.get('user_id')
        room_id = validated_data.get('room_id')
        
        model = Booking.objects.check_user_out(
                user_id = user_id,
                room_id = room_id
            )
        return model
        
class RoomStatusSerializer(serializers.ModelSerializer):
    availability_status = serializers.BooleanField(validators=[checkBool])
    reason = serializers.CharField(max_length=300, min_length=1, write_only=True)
    
    class Meta:
        model=RoomAllocation
        fields = ['id', 'availability_status', 'room', 'reason']
        
        
    def validate(self, attrs):
        
        return attrs

    def update(self, instance, validated_data):
        availability_status = validated_data.get('availability_status')
        reason = validated_data.get('reason')
       
        if instance.availability_status and availability_status:
            raise serializers.ValidationError(_("This room is already available"))
        
        elif not instance.availability_status and not availability_status:
            raise serializers.ValidationError(_("This room is already unavailable"))
        
        if instance.status == RoomStatus.CHECKED_IN.value or instance.status == RoomStatus.BOOKED.value:
            raise serializers.ValidationError(_("This room is in use"))
       
        if not availability_status:
            UNAVAILABLE_STATUS = RoomStatus.UNAVAILABLE.value
            status_Id = RoomStatus[RoomStatus(UNAVAILABLE_STATUS).name].value
            instance.availability_status = availability_status
            instance.status = status_Id  
            
            room_status_change = RoomStatusChange(room=instance.room, reason=reason)
            room_status_change.save()
            instance.save()
            return instance 
        
        AVAILABLE_STATUS = RoomStatus.AVAILABLE.value
        status_Id = RoomStatus[RoomStatus(AVAILABLE_STATUS).name].value
        instance.availability_status = availability_status
        instance.status = status_Id  
        instance.save()
        
        room_status_change = RoomStatusChange(room=instance.room, reason=reason)
        room_status_change.save()
        instance.save()
        
        return instance         
        
       
    
class BookingCreateSerializer(serializers.Serializer):
    room_id=serializers.IntegerField(write_only=True)
    user_id=serializers.CharField(max_length=100, min_length=6, write_only=True)
    start_date=serializers.DateField(write_only=True)
    end_date=serializers.DateField(write_only=True)
    

    class Meta:
        fields = "__all__"
        
    def validate(self, attrs):
        if not attrs.get("room_id"):
             raise serializers.ValidationError("Room Id is required")
        if not attrs.get("user_id"):
             raise serializers.ValidationError("Current user id is required")
        if not attrs.get("start_date"):
             raise serializers.ValidationError("Start date id is required")
        if not attrs.get("end_date"):
             raise serializers.ValidationError("End date user id is required")
       
        return attrs

    def create(self, validated_data):
    
        booking = Booking.objects.create_booking_1(
                room_id = validated_data.get('room_id'),
                user_id = validated_data.get('user_id'),
                start_date = validated_data.get('start_date'),
                end_date = validated_data.get('end_date'),
            )
        
        return booking
    
  
class DashboardBootstrapSerializer(serializers.Serializer):
    room_count = serializers.IntegerField(read_only=True)
    checkin_count = serializers.IntegerField(read_only=True)
    average_checkins_per_day = serializers.IntegerField(read_only=True)
    checkout_count = serializers.IntegerField(read_only=True)
    guest_count = serializers.IntegerField(read_only=True)
    rating_average = serializers.DecimalField(max_digits=4, decimal_places=1, read_only=True)
    
    class Meta:
        fields = ['room_count', 'checkin_count', 'average_checkins_per_day', 'checkout_count', 'guest_count', 'rating_average']
        
        
class RoomBootstrapSerializer(serializers.Serializer):
    room_count = serializers.IntegerField(read_only=True)
    available_rooms = serializers.ListSerializer(child=serializers.CharField())
    unavailable_rooms = serializers.ListSerializer(child=serializers.CharField())
    booked_rooms = serializers.ListSerializer(child=serializers.CharField())
    
    class Meta:
        fields = ['room_count', 'available_rooms', 'unavailable_rooms', 'booked_rooms']
 

class UserCheckoutSerializer(serializers.Serializer):
    id_list = serializers.ListSerializer(child=serializers.IntegerField())

    class Meta:
        fields = ('id_list',)
        
    def validate(self, attrs):
        
        return attrs

    def update(self, validated_data):
        model = Booking.objects.check_user_out_ext(
               id_list = validated_data.get("id_list"),
            )
        return model
        
        
class BookedRoomSerializer(serializers.Serializer):
    room_id = serializers.IntegerField()
    room = serializers.CharField()
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    check_in = serializers.DateTimeField()
    check_out = serializers.DateTimeField()
    
    
    
class RoomAllocationHistorySerializer(serializers.Serializer):
    room_details = serializers.DictField()
    booking_history = serializers.ListField(child=serializers.DictField())
    status_changes = serializers.ListField(child=serializers.DictField())
    

class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ("id", 'user', "check_in", "check_out", "start_date", "end_date", "date_created")  # Include other fields as needed


class RoomStatusChangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomStatusChange
        fields = ("id", "room", "reason", "created_by")