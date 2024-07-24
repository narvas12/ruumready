import io
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.utils import timezone
from backend import settings
from common.notification import Notification
from reservations.utils import send_check_in_email
from rooms.models import Room
from .serializers import  BookingCreateSerializer, BookingsHistorySerializer, CheckInSerializer, CheckOutSerializer, DashboardBootstrapSerializer, MultipleCheckInSerializer, RoomAllocationHistorySerializer, RoomBootstrapSerializer, RoomStatusSerializer, RoomByStatusSerializer, UserCheckoutSerializer
from common.renderers import ApiCustomRenderer
from rest_framework.exceptions import *
from django.apps import apps
from .models import *
from django.db.models import Q
from rest_framework.permissions import IsAuthenticated
from common.pagination import CustomPageNumberPagination
import csv
from django.http import HttpResponse, FileResponse
from reportlab.pdfgen import canvas
from reportlab.lib.units  import inch
from reportlab.lib.pagesizes import letter
from asgiref.sync import async_to_sync


# Create your views here.

class RoomsForCheckoutView(GenericAPIView):
    serializer_class = RoomByStatusSerializer
    renderer_classes = (ApiCustomRenderer,)
    #permission_classes = [IsAuthenticated]

    def get(self, request):
            param = self.request.query_params.get('param', None)
            
            queryset = RoomAllocation.objects.get_rooms_for_checkout(param)
            serializer = self.serializer_class(queryset, many=True)
            if serializer.data:
                data = serializer.data
                return Response({
                    'payload': data
                }, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SingleBookingView(GenericAPIView):
    serializer_class = BookingsHistorySerializer
    renderer_classes = (ApiCustomRenderer,)
    #permission_classes = [IsAuthenticated]

    def get(self, request, id):
       
        record = Booking.objects.filter(**{"id": id})
        if not record:
            raise NotFound("Record does not exist")
        record = record[0]
        serializer = self.serializer_class(record, many=False)
    
        if serializer.data:
            room=serializer.data
            return Response({
                'payload':room,
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class BookingsHistoryDocView(GenericAPIView):
    serializer_class = BookingsHistorySerializer
    renderer_classes = (ApiCustomRenderer,)
    #permission_classes = [IsAuthenticated]
    pagination_class = CustomPageNumberPagination

    def get(self, request, file_type):
        ACCEPTED_PARAMS = ["pdf", "csv", "xlsx"]
        if file_type not in ACCEPTED_PARAMS:
             return Response(data={}, status=status.HTTP_200_OK)
         
        date_from = self.request.query_params.get('date_from', None)
        date_to = self.request.query_params.get('date_to', None)
            
        match file_type:
            case "pdf":
                bookings = Booking.objects.get_rooms_overview_for_doc(date_from, date_to)
                data = [["Name", "Age", "City"], ["John", 30, "New York"], ["Jane", 25, "Los Angeles"]]
                
                # Create PDF content
                response = HttpResponse(content_type='application/pdf')
                response['Content-Disposition'] = 'attachment; filename=report.pdf'
                
                pdf = canvas.Canvas(response)

                # Add content to the PDF
                pdf.setFont("Helvetica", 12)
                pdf.drawString(50, 750, "Your Report Title")

                # Add table data
                table_data = data
                table_width = 500
                table_height = len(data) * 20

                for i, row in enumerate(table_data):
                    for j, cell in enumerate(row):
                        pdf.drawString(table_width * j / len(row) + 50, 730 - i * 20, str(cell))

                pdf.save()

                return response


                buf = io.BytesIO()
                c = canvas.Canvas(buf, pagesize=letter, bottomup=0)
                
                text_obj = c.beginText()
                text_obj.setTextOrigin(inch, inch)
                text_obj.setFont("Helvetica", 12)

                lines = ["Room ID", "Room Name", "Type", "Guest ID", "Phone Number", "Check-In Time", "Check-Out Time", "Status"]
                for line in lines:
                    text_obj.textLine(line)
               
                c.drawText(text_obj)
                c.showPage()
                c.save()
                buf.seek(0)

                return FileResponse(buf, as_attachment=True, filename="report.pdf")
            
            case "csv":
                response = HttpResponse(content_type='text/csv')
                response["Content-Disposition"] = 'attachement; filename=history.csv'
                
                writer = csv.writer(response)
                bookings = Booking.objects.get_rooms_overview_for_doc(date_from, date_to)

                writer.writerow(["Room ID", "Room Name", "Type", "Guest ID", "Phone Number", "Check-In Time", "Check-Out Time", "Status"])
                for booking in bookings:
                    writer.writerow([booking.room.room_id, booking.room.room_name, booking.room.apartment_type.apartment_type, booking.user.guest_id, booking.user.mobile, booking.check_in, booking.check_out, booking.check_out])
                return response
            
            case "xlsx":  
                pass

class BookingsHistoryView(GenericAPIView):
    serializer_class = BookingsHistorySerializer
    renderer_classes = (ApiCustomRenderer,)
    #permission_classes = [IsAuthenticated]
    pagination_class = CustomPageNumberPagination

    def get(self, request):
            queryset = Booking.objects.get_rooms_overview()
            page = self.paginate_queryset(queryset)  # Apply pagination
            serializer = self.serializer_class(page, many=True)
            if serializer.is_valid:
                return self.get_paginated_response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        
        
class RoomHistoryView(APIView):
    def get(self, request, room_id):
        try:
            room_history_data = RoomAllocation.objects.get_room_history(room_id)
            serializer = RoomAllocationHistorySerializer(room_history_data)
            # Convert the serialized data to a list
            data_list = [serializer.data]
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Room.DoesNotExist:
            return Response(
                {"error": "Room not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CurrentBookingHistoryView(GenericAPIView):
    serializer_class = BookingsHistorySerializer
    renderer_classes = (ApiCustomRenderer,)
    #permission_classes = [IsAuthenticated]
    pagination_class = CustomPageNumberPagination

    def get(self, request):
            queryset = Booking.objects.get_current_rooms_overview()
            page = self.paginate_queryset(queryset)  # Apply pagination
            serializer = self.serializer_class(page, many=True)
            if serializer.is_valid:
                return self.get_paginated_response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
class UserBookingHistoryView(GenericAPIView):
    serializer_class = BookingsHistorySerializer
    renderer_classes = (ApiCustomRenderer,)
    #permission_classes = [IsAuthenticated]
    pagination_class = CustomPageNumberPagination

    def get(self, request, user_id):
            queryset = Booking.objects.get_user_rooms_overview(user_id=user_id)
            page = self.paginate_queryset(queryset)  # Apply pagination
            serializer = self.serializer_class(page, many=True)
            if serializer.is_valid:
                return self.get_paginated_response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
   
class RoomAllocationsView(GenericAPIView):
    serializer_class = RoomByStatusSerializer
    renderer_classes = (ApiCustomRenderer,)
    #permission_classes = [IsAuthenticated]
    pagination_class = CustomPageNumberPagination

    def get(self, request):
            room_status = self.request.query_params.get('status', None)
            
            queryset = RoomAllocation.objects.get_rooms(room_status)
            page = self.paginate_queryset(queryset)  # Apply pagination
            serializer = self.serializer_class(page, many=True)
            if serializer.is_valid:
                return self.get_paginated_response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
         
class RoomStatusView(GenericAPIView):
    serializer_class = RoomStatusSerializer
    renderer_classes = (ApiCustomRenderer,)
    #permission_classes = [IsAuthenticated]

    def patch(self, request, id):
        record = RoomAllocation.objects.filter(**{'room_id': id})
        if not record:
            raise NotFound("Room with that Id does not exist")
            
        record = record[0]
        serializer = self.serializer_class(instance=record, data=request.data)
    
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            data=serializer.data
            return Response({
                'payload': {},
            }, status=status.HTTP_200_OK)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class BookRoomView(GenericAPIView):
    serializer_class = BookingCreateSerializer
    renderer_classes = (ApiCustomRenderer,)
    #permission_classes = [IsAuthenticated]

    def post(self, request):
      
        booking = request.data
        serializer=self.serializer_class(data=booking)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            room_data=serializer.data
            return Response({
                'payload': None,
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class MultipleCheckInView(GenericAPIView):
    serializer_class = MultipleCheckInSerializer
    renderer_classes = (ApiCustomRenderer,)
    # permission_classes = [IsAuthenticated]  # Uncomment if authentication is required

    def patch(self, request):
        User = apps.get_model('accounts', 'User')
        Room = apps.get_model('rooms', 'Room')  # Adjust this based on your app structure
        Booking = apps.get_model('reservations', 'Booking')

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_id = serializer.validated_data.get("user_id")
        room_ids = serializer.validated_data.get("room_ids")

        user_instance = User.objects.filter(guest_id=user_id).first()
        if not user_instance:
            raise ValidationError("User with that ID does not exist")

        bookings = Booking.objects.filter(room_id__in=room_ids, user_id=user_instance.id)
        if not bookings.exists():
            raise ValidationError("User must book the specified rooms before check-in")

        checkin_time = timezone.now()
        to_email = "devcaliban@gmail.com"
        email_subject = "New Check-In"
        user_full_name = user_instance.get_full_name() if hasattr(user_instance, 'get_full_name') else f"{user_instance.first_name} {user_instance.last_name}"

        room_details = Room.objects.filter(id__in=room_ids).values('room_id', 'room_name')
        room_details_dict = {room['room_id']: room['room_name'] for room in room_details}
        
        already_checked_in_rooms = []
        successfully_checked_in_rooms = []

        for booking in bookings:
            if booking.check_in:
                already_checked_in_rooms.append(booking.room_id)
            else:
                booking.check_in = checkin_time
                booking.save()
                successfully_checked_in_rooms.append(booking.room_id)
        
        response_data = {
            'message': 'Rooms checked in successfully',
            'already_checked_in_rooms': already_checked_in_rooms,
            'successfully_checked_in_rooms': successfully_checked_in_rooms
        }

        # Prepare email content and send notification if there are new check-ins
        if successfully_checked_in_rooms:
            room_details_list = [f"{room_details_dict.get(room_id)} - {room_id}" for room_id in successfully_checked_in_rooms]
            already_checked_in_details = [f"{room_details_dict.get(room_id)} - {room_id}" for room_id in already_checked_in_rooms]
            
            html_content = f"""
            The following rooms have been checked in: {', '.join(room_details_list)}
            User: {user_full_name}
            Check-in Time: {checkin_time}
            """
            if already_checked_in_rooms:
                html_content += f"<br>Note: The following rooms were already checked in: {', '.join(already_checked_in_details)}"
            
            async_to_sync(Notification.send_email_async)(to_email=to_email, subject=email_subject, html_content=html_content)
        
        # Return different response based on check-in status
        if successfully_checked_in_rooms:
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            return Response({
                'message': 'All specified rooms have already been checked in',
                'already_checked_in_rooms': already_checked_in_rooms
            }, status=status.HTTP_400_BAD_REQUEST)
       
       
class CheckInView(GenericAPIView):
    serializer_class = CheckInSerializer
    renderer_classes = (ApiCustomRenderer,)
    #permission_classes = [IsAuthenticated]

    def patch(self, request):
        User = apps.get_model('accounts', 'User')
       
        user_instance = User.objects.filter(**{'guest_id': request.data.get("user_id")})
        if not user_instance:
            raise ValidationError("User with that id does not exist")
        user_instance = user_instance[0]

        record = Booking.objects.filter(Q(room_id = request.data.get("room_id")) & Q(user_id = user_instance.id))
        if not record:
            raise ValidationError("User must book a room before check-in")
        record = record[0]

        serializer=self.serializer_class(instance=record, data=request.data)
        if serializer.is_valid(raise_exception=True):
             serializer.update(record, request.data)
             room_data=serializer.data
             return Response({
                    'payload':None,
                }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)    
       
    
class CheckOutView(GenericAPIView):
    serializer_class = CheckOutSerializer
    renderer_classes = (ApiCustomRenderer,)
    #permission_classes = [IsAuthenticated]

    def patch(self, request):
        User = apps.get_model('accounts', 'User')
        user_instance = User.objects.filter(**{'guest_id': request.data.get("user_id")})
        if not user_instance:
            raise ValidationError("User with that id does not exist")
        user_instance = user_instance[0]
        
        record = Booking.objects.filter(Q(room_id = request.data.get("room_id")) & Q(user_id = user_instance.id))
        if not record:
            raise ValidationError("User must book a room before check-out")
        record = record[0]
        serializer=self.serializer_class(instance=record, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.update(record, request.data)
            room_data=serializer.data
            return Response({
                'payload':None,
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DashboardBootstrapView(GenericAPIView):
    serializer_class = DashboardBootstrapSerializer
    renderer_classes = (ApiCustomRenderer,)

    def get(self, request):
        records = RoomAllocation.objects.get_dashboard_bootstrap_data()
      
        serializer = self.serializer_class(records)
        if serializer.data:
              return Response({
                'payload': serializer.data,
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class RoomBootstrapView(GenericAPIView):
    serializer_class = RoomBootstrapSerializer
    renderer_classes = (ApiCustomRenderer,)

    def get(self, request):
        records = RoomAllocation.objects.get_room_bootstrap_data()
      
        serializer = self.serializer_class(records)
        if serializer.data:
              return Response({
                'payload': serializer.data,
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class UserCheckoutView(GenericAPIView):
    serializer_class = UserCheckoutSerializer
    renderer_classes = (ApiCustomRenderer,)
    #permission_classes = [IsAuthenticated]

    def patch(self, request):
        serializer=self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.update(validated_data=request.data)
            data=serializer.data
            return Response({
                'payload':None,
             
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


