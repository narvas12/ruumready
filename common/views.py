from django.shortcuts import render
from rest_framework.generics import GenericAPIView
from .pagination import CustomPageNumberPagination
from .serializers import RatingCreateSerializer, RatingSerializer
from .renderers import ApiCustomRenderer
from rest_framework.response import Response
from rest_framework import status
from .models import Rating

# Create your views here.

class RatingCreateView(GenericAPIView):
    serializer_class = RatingCreateSerializer
    renderer_classes = (ApiCustomRenderer,)

    def post(self, request):
        rating = request.data
        serializer=self.serializer_class(data=rating)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            room_data=serializer.data
            return Response({
                'payload':None,
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class RatingsView(GenericAPIView):
    serializer_class = RatingSerializer
    renderer_classes = (ApiCustomRenderer,)
    pagination_class = CustomPageNumberPagination

    def get(self, request):
        rating_type = self.request.query_params.get('rating_type', None)
        records = Rating.objects.get_ratings(rating_type)
        
        page = self.paginate_queryset(records)  # Apply pagination
        serializer = self.serializer_class(page, many=True)
        if serializer.is_valid:
                return self.get_paginated_response(serializer.data) # Return paginated response
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
