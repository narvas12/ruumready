from multiprocessing import context
from django.shortcuts import render
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import ApartmentTypeCreateSerializer, ApartmentTypeSerializer, RoomCreateSerializer, RoomSerializer
from common.renderers import ApiCustomRenderer
from rest_framework.exceptions import *
from rest_framework.pagination import PageNumberPagination
from common.pagination import CustomPageNumberPagination
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .models import *
# Create your views here.

class RoomCreateView(GenericAPIView):
    serializer_class = RoomCreateSerializer
    renderer_classes = (ApiCustomRenderer,)
    #permission_classes = [IsAuthenticated]

    def post(self, request):
        room = request.data
        serializer=self.serializer_class(data=room)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            room_data=serializer.data
            return Response({
                'payload':room_data,
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
   
class RoomsView(GenericAPIView):
    serializer_class = RoomSerializer
    renderer_classes = (ApiCustomRenderer,)
    #permission_classes = [IsAuthenticated]
    pagination_class = CustomPageNumberPagination
    
    def get(self, request):
        queryset = Room.objects.get_all_rooms()
        page = self.paginate_queryset(queryset)  # Apply pagination
        serializer = self.serializer_class(page, many=True)
        
        if serializer.is_valid:
            return self.get_paginated_response(serializer.data) # Return paginated response
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RoomView(GenericAPIView):
    serializer_class = RoomSerializer
    renderer_classes = (ApiCustomRenderer,)
    #permission_classes = [IsAuthenticated]

    def get(self, request, id):
        record = Room.objects.get_room(room_id=id)
        serializer = self.serializer_class(record, many=False)
    
        if serializer.data:
            room=serializer.data
            return Response({
                'payload':room,
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
class RoomUpdateView(GenericAPIView):
    serializer_class = RoomCreateSerializer
    renderer_classes = (ApiCustomRenderer,)
    #permission_classes = [IsAuthenticated]

    def patch(self, request, id):
        record = Room.objects.get_room(room_id=id)
        serializer = self.serializer_class(instance=record, data=request.data)
        
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            apartment_type_data=serializer.data
            return Response({
                'payload':apartment_type_data,
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RoomDeleteView(GenericAPIView):
    serializer_class = RoomSerializer
    renderer_classes = (ApiCustomRenderer,)
    permission_classes = [IsAuthenticated]

    def delete(self, request, id):
        
        Room.objects.delete_room(room_id=id)

        return Response({
        'payload':None,
        }, status=status.HTTP_200_OK)

class ApartmentTypeCreateView(GenericAPIView):
    serializer_class = ApartmentTypeCreateSerializer
    renderer_classes = (ApiCustomRenderer,)
    #permission_classes = [IsAuthenticated]

    def post(self, request):
        apartment_type = request.data
        serializer=self.serializer_class(data=apartment_type)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            apartment_type_data=serializer.data
            return Response({
                'payload':apartment_type_data,
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class ApartmentTypesView(GenericAPIView):
    serializer_class = ApartmentTypeSerializer
    renderer_classes = (ApiCustomRenderer,)
    #permission_classes = [IsAuthenticated]
    pagination_class = CustomPageNumberPagination

    def get(self, request):
        queryset = ApartmentType.objects.get_all_apartment_types()
        page = self.paginate_queryset(queryset)  # Apply pagination
        serializer = self.serializer_class(page, many=True)
        
        if serializer.is_valid:
            return self.get_paginated_response(serializer.data) # Return paginated response
       
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class ApartmentTypeView(GenericAPIView):
    serializer_class = ApartmentTypeSerializer
    renderer_classes = (ApiCustomRenderer,)
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        record = ApartmentType.objects.get_apartment_type(apartment_type_id=id)
        serializer = self.serializer_class(record, many=False)
    
        if serializer.data:
            list=serializer.data
            return Response({
                'payload':list,
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class ApartmentTypeUpdateView(GenericAPIView):
    serializer_class = ApartmentTypeSerializer
    renderer_classes = (ApiCustomRenderer,)
    permission_classes = [IsAuthenticated]

    def patch(self, request, id):
        record = ApartmentType.objects.get_apartment_type(apartment_type_id=id)

        serializer = self.serializer_class(instance=record, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            apartment_type_data=serializer.data
            return Response({
                'payload':apartment_type_data,
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class ApartmentTypeDeleteView(GenericAPIView):
    serializer_class = ApartmentTypeSerializer
    renderer_classes = (ApiCustomRenderer,)
    permission_classes = [IsAuthenticated]

    def delete(self, request, id):
        ApartmentType.objects.delete_apartment_type(apartment_type_id=id)
        
        return Response({
            'payload':None,
        }, status=status.HTTP_200_OK)
       