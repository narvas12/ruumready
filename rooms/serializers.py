from .models import ApartmentType, Room
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed, ValidationError



class ApartmentTypeCreateSerializer(serializers.ModelSerializer):
    apartment_type = serializers.CharField(max_length=50, min_length=1)
    description = serializers.CharField(max_length=255)

    class Meta:
        model=ApartmentType
        fields = [ 'id','apartment_type', 'description']

    def validate(self, attrs):
        supplied_apartment_type = str(attrs.get("apartment_type"))

        if not supplied_apartment_type:
            raise serializers.ValidationError("Apartment type is required")
        if ApartmentType.objects.filter(apartment_type=supplied_apartment_type).exists():
            raise ValidationError("Apartment Type already exist")

        return attrs

    def create(self, validated_data):
        apartment_type = ApartmentType.objects.create_apartment_type(
            apartment_type = validated_data.get('apartment_type'),
            description = validated_data.get('description'),
            )
        return apartment_type


class ApartmentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model=ApartmentType
        fields = [ 'id','apartment_type', 'description']

class RoomCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model=Room
        fields = ['id', 'room_id', 'room_name', 'description', 'amount_daily', 'apartment_type']

        
    def validate(self, attrs):
        if not attrs.get("room_id"):
             raise serializers.ValidationError("Room Id is required")
        if not attrs.get("room_name"):
             raise serializers.ValidationError("Room name is required")

        return attrs

    def create(self, validated_data):
        apartment_type_id = validated_data.get('apartment_type').id

        apartment_type = ApartmentType.objects.get(id=apartment_type_id)
        room= Room.objects.create_room(
                room_id = validated_data.get('room_id'),
                room_name = validated_data.get('room_name'),
                apartment_type = apartment_type,
                description = validated_data.get('description'),
                amount_daily = validated_data.get('amount_daily')
            )
        return room
    
    
    def update(self, instance, validated_data):
        instance = Room.objects.update_room(instance=instance, validated_data=validated_data)
        
        return instance


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model=Room
        fields = ['id', 'room_id', 'room_name', 'description', 'amount_daily', 'apartment_type']

        read_only_fields = ('apartment_type', )
        depth = 1
        
        #  