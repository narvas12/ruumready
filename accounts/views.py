from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from accounts.models import OneTimePassword
from common.emailing import send_email_using_sendgrid
from reservations.models import Booking
from reservations.serializers import BookedRoomSerializer, BookingSerializer
from .serializers import *
from rest_framework import status
from rest_framework.views import APIView
from common.renderers import ApiCustomRenderer
from .utils.utils import send_generated_otp_to_email
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import smart_str, DjangoUnicodeDecodeError
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import User
from common.pagination import CustomPageNumberPagination
# Create your views here.


#AUTH VIEWS
class RegisterAndBookWalkInView(GenericAPIView):
    serializer_class = RegisterAndBookWalkInSerializer
    renderer_classes = (ApiCustomRenderer,)

    def post(self, request):
        registration_data = request.data
        serializer=self.serializer_class(data=registration_data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            data=serializer.data
            return Response({
                'data':data,
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
  
class RegisterWalkInView(GenericAPIView):
    serializer_class = RegisterWalkInSerializer
    renderer_classes = (ApiCustomRenderer,)

    def post(self, request):
        user = request.data
        serializer=self.serializer_class(data=user)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            user_data=serializer.data
            return Response({
                'user_data':user_data,
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class RegisterView(GenericAPIView):
    serializer_class = UserRegisterSerializer
    renderer_classes = (ApiCustomRenderer,)

    def post(self, request):
        user = request.data
        serializer=self.serializer_class(data=user)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            user_data=serializer.data
            #send_generated_otp_to_email(user_data['email'], request)
            return Response({
                'user_data':user_data,
                'message':'thanks for signing up a passcode has be sent to verify your email'
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class AdminRegisterView(GenericAPIView):
    serializer_class = AdminRegisterSerializer
    renderer_classes = (ApiCustomRenderer,)

    def post(self, request):
        user = request.data
        serializer=self.serializer_class(data=user)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            user_data=serializer.data
            return Response({
                'data':user_data,
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



# addedd by Eze
class AdminLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = AdminLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'is_staff': user.is_staff,  # Include is_staff status in the response
        })


class VerifyUserEmail(GenericAPIView):
    def post(self, request):
        try:
            passcode = request.data.get('otp')
            user_pass_obj=OneTimePassword.objects.get(otp=passcode)
            user=user_pass_obj.user
            if not user.is_verified:
                user.is_verified=True
                user.save()
                return Response({
                    'message':'account email verified successfully'
                }, status=status.HTTP_200_OK)
            return Response({'message':'passcode is invalid user is already verified'}, status=status.HTTP_204_NO_CONTENT)
        except OneTimePassword.DoesNotExist as identifier:
            return Response({'message':'passcode not provided'}, status=status.HTTP_400_BAD_REQUEST)


class LoginUserView(GenericAPIView):
    serializer_class=LoginSerializer
    renderer_classes = (ApiCustomRenderer,)
    
    def post(self, request):
        serializer= self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PasswordResetRequestView(GenericAPIView):
    serializer_class = PasswordResetRequestSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'message': 'Email not found'}, status=status.HTTP_400_BAD_REQUEST)

        # Generate a password reset token
        token_generator = PasswordResetTokenGenerator()
        uidb64 = urlsafe_base64_encode(smart_str(user.pk)).decode()
        token = token_generator.make_token(user)

        # Construct email content
        subject = 'Password Reset Request on My Platform'
        email_body = f'Hi {user.username},\n You have requested a password reset for your account on My Platform. \n' \
                     f'To complete the reset, please click the following link: \n' \
                     f'http://your-domain.com/password-reset/{uidb64}/{token} \n' \
                     f'This link will expire in a limited time. \n' \
                     f'If you did not request a password reset, please ignore this email.'

        # Send email using SendGrid
        send_email_using_sendgrid(subject, email_body, email)  # Call the function you defined earlier

        return Response({'message': 'We have sent you a code to reset your password'}, status=status.HTTP_200_OK)




class PasswordResetConfirm(GenericAPIView):
    def get(self, request, uidb64, token):
        try:
            user_id = smart_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=user_id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                return Response({'message': 'Token is invalid or has expired'}, status=status.HTTP_401_UNAUTHORIZED)

            return Response({'success': True}, status=status.HTTP_200_OK)

        except DjangoUnicodeDecodeError:
            return Response({'message': 'Token is invalid or has expired'}, status=status.HTTP_401_UNAUTHORIZED)
        except User.DoesNotExist:
            return Response({'message': 'Invalid user ID'}, status=status.HTTP_400_BAD_REQUEST)
        
        

class SetNewPasswordView(GenericAPIView):
    serializer_class = SetNewPasswordSerializer

    def patch(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        token = data['token']
        uidb64 = data.get('uidb64') 

        try:
            user_id = smart_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=user_id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                return Response({'message': 'Token is invalid or has expired'}, status=status.HTTP_401_UNAUTHORIZED)

            user.set_password(data['password'])
            user.save()

            return Response({'success': True}, status=status.HTTP_200_OK)

        except (ValueError, User.DoesNotExist):
            return Response({'message': 'Invalid user or token'}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return Response({'message': 'An error occurred. Please try again later.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class TestingAuthenticatedReq(GenericAPIView):
    permission_classes=[IsAuthenticated]
    renderer_classes = (ApiCustomRenderer,)
    

    def get(self, request):

        data={
            'msg':'its works'
        }
        return Response(data, status=status.HTTP_200_OK)


class LogoutApiView(GenericAPIView):
    serializer_class=LogoutUserSerializer
    renderer_classes = (ApiCustomRenderer,)

    def post(self, request):
        serializer=self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'message':"Logout is succesful"}, status=status.HTTP_200_OK)
 
 
class UserView(GenericAPIView):
    serializer_class = UserSerializer
    renderer_classes = (ApiCustomRenderer,)

    def get(self, request):
        param = self.request.query_params.get('param', None)
        
        user = User.objects.get_user(param=param)
        user_serializer = self.serializer_class(user, many=False)
        
        if user_serializer.data:
            user_data = user_serializer.data
            
            # Fetch booked rooms using the related name 'bookings' from the User model
            booked_rooms = Booking.objects.get_user_booked_rooms(user_id=user.id)
            print(booked_rooms)
            booking_serializer = BookedRoomSerializer(booked_rooms, many=True)  # Assuming BookingSerializer is defined
            
            return Response({
                'payload': user_data,
                'booked_rooms': booking_serializer.data,  # Include booked rooms data in the response
                'message': 'User fetched successfully with booked rooms'
            }, status=status.HTTP_200_OK)
        
        return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserByPhoneView(GenericAPIView):
    serializer_class = UserSerializer
    renderer_classes = (ApiCustomRenderer,)
    #permission_classes = [IsAuthenticated]

    def get(self, request, mobile):
        record = User.objects.get_user_by_phone(mobile=mobile)
        serializer = self.serializer_class(record, many=False)
    
        if serializer.data:
            user=serializer.data
            return Response({
                'payload':user,
          
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class UsersView(GenericAPIView):
    serializer_class = UserSerializer
    renderer_classes = (ApiCustomRenderer,)
    #permission_classes = [IsAuthenticated]
    pagination_class = CustomPageNumberPagination
    
    def get(self, request):
        queryset = User.objects.get_all_users()
        page = self.paginate_queryset(queryset)  # Apply pagination
        serializer = self.serializer_class(page, many=True)
        
        if serializer.is_valid:
            return self.get_paginated_response(serializer.data) # Return paginated response
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

 
#VERIFICATION VIEWS
class VerificationView(GenericAPIView):
    serializer_class = VerificationSerializer
    renderer_classes = (ApiCustomRenderer,)
    #permission_classes = [IsAuthenticated]

    def get(self, request, mobile):
        record = MobileVerification.objects.get_verified_userdetails_by_phone(phone_number=mobile)
        serializer = self.serializer_class(record, many=False)
    
        if serializer.data:
            verified_user=serializer.data
            return Response({
                'payload':verified_user,
              
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
 
class VerifiedUserDetailsView(GenericAPIView):
    serializer_class = VerificationSerializer
    renderer_classes = (ApiCustomRenderer,)
    #permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        record = User.objects.get_verified_user_details(user_id=user_id)
        serializer = self.serializer_class(record, many=False)
    
        if serializer.data:
            verified_details=serializer.data
            return Response({
                'payload':verified_details,
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    