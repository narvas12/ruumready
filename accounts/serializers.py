from .models import User, MobileVerification, OneTimePassword
from rest_framework import serializers
from string import ascii_lowercase, ascii_uppercase
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed, ValidationError
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str, force_str, smart_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from .utils.utils import generateGuestId, send_generated_otp_to_email, send_normal_email
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from django.utils.translation import gettext_lazy as _

class RegisterAndBookWalkInSerializer(serializers.ModelSerializer):
    valid_id_doc = serializers.FileField(required=False)
    room=serializers.IntegerField(write_only=True)
    start_date=serializers.DateField(write_only=True)
    end_date=serializers.DateField(write_only=True)

    class Meta:
        model=User
        fields = ['guest_id', 'email', 'mobile', 'full_name',  'start_date', 'end_date', 'room', 'valid_address',  'valid_id', 'occupation', 'date_joined', 'valid_id_doc']

    def validate(self, attrs):
        if not attrs.get('full_name'):
            raise serializers.ValidationError(_("Fullname is required"))
        if not attrs.get('mobile'):
            raise serializers.ValidationError(_("Mobile number is required"))
        if not attrs.get('start_date'):
            raise serializers.ValidationError(_("start_date is required"))  
        if not attrs.get('end_date'):
            raise serializers.ValidationError(_("end_date is required"))
        if not attrs.get('room'):
            raise serializers.ValidationError(_("room is required"))
        # password=attrs.get('password', '')
        # password2 =attrs.get('password2', '')
        # if password != password2:
        #     raise serializers.ValidationError("passwords do not match")
         
        return attrs

    def create(self, validated_data):
        
        recs = User.objects.filter(guest_id__startswith= 'LUX')
        if len(recs) > 0:
            last_created_user = recs.order_by('-date_created')[0]
            last_created_user_guest_id = last_created_user.guest_id
            print(last_created_user_guest_id)
            user =  User.objects.create_walkin_user(
                mobile = validated_data.get('mobile'),
                full_name = validated_data.get('full_name'),
                password = validated_data.get("password"),
                guest_id = generateGuestId(last_created_user_guest_id),
                email = validated_data.get("email"),
                valid_address = validated_data.get("valid_address"),
                valid_id = validated_data.get("valid_id"),
                occupation = validated_data.get("occupation"),
                start_date = validated_data.get("start_date"),
                end_date = validated_data.get("end_date"),
                room_id = validated_data.get("room"),
                doc = validated_data.get("valid_id_doc"),
                
            )
            return user
           
        else:
            FIRST_GUEST_ID = "LUX-001"
            user = User.objects.create_walkin_user(
                mobile = validated_data['mobile'],
                full_name = validated_data.get('full_name'),
                password = validated_data.get("email"),
                guest_id = FIRST_GUEST_ID,
                email = validated_data.get("email"),
                valid_address = validated_data.get("valid_address"),
                valid_id = validated_data.get("valid_id"),
                occupation = validated_data.get("occupation"),
                start_date = validated_data.get("start_date"),
                end_date = validated_data.get("end_date"),
                room_id = validated_data.get("room"),
                doc = validated_data.get("valid_id_doc"),
                
            )
            return user


#AUTH SERIALIZERS
class RegisterWalkInSerializer(serializers.ModelSerializer):

    class Meta:
        model=User
        fields = ['guest_id', 'email', 'mobile', 'full_name', 'address',  'identification_number', 'occupation']

    def validate(self, attrs):
        if not attrs.get('full_name'):
            raise serializers.ValidationError(_("Fullname is required"))
        if not attrs.get('mobile'):
            raise serializers.ValidationError(_("Mobile number is required"))
        # password=attrs.get('password', '')
        # password2 =attrs.get('password2', '')
        # if password != password2:
        #     raise serializers.ValidationError("passwords do not match")
         
        return attrs

    def create(self, validated_data):
        
        if User.objects.exists():
            #latest_object = User.objects.order_by('guest_id')[0]
            user_records = User.objects.filter(guest_id__startswith= 'LUX')
            last_created_user = user_records.order_by('-date_created')[0]
            last_created_user_guest_id = last_created_user.guest_id
            user =  User.objects.create_walkin_user(
                mobile = validated_data.get('mobile'),
                full_name = validated_data.get('full_name'),
                password = validated_data.get("email"),
                guest_id = generateGuestId(last_created_user_guest_id),
                email = validated_data.get("email"),
                address = validated_data.get("address"),
                identification_number = validated_data.get("identification_number"),
                occupation = validated_data.get("occupation")
            )
            return user
           
        else:
            FIRST_GUEST_ID = "LUX-001"
            user = User.objects.create_walkin_user(
                mobile = validated_data['mobile'],
                full_name = validated_data.get('full_name'),
                password = validated_data.get("email"),
                guest_id = FIRST_GUEST_ID,
                email = validated_data.get("email"),
                address = validated_data.get("address"),
                identification_number = validated_data.get("identification_number"),
                occupation = validated_data.get("occupation")
            )
            return user

class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=68, min_length=6, write_only=True)
    password2= serializers.CharField(max_length=68, min_length=6, write_only=True)

    class Meta:
        model=User
        fields = ['guest_id', 'email', 'mobile', 'full_name', 'password', 'password2', 'address', 'identication_number']

    def validate(self, attrs):
        password=attrs.get('password', '')
        password2 =attrs.get('password2', '')
        if password != password2:
            raise serializers.ValidationError("passwords do not match")
         
        return attrs

    def create(self, validated_data):
        
        #latest_object1 = User.objects.latest('date_created')
        if User.objects.exists():
            latest_object = User.objects.order_by('-id')[0]
            last_guest_id = latest_object.guest_id
            user = User.objects.create_walkin_user(
                mobile = validated_data.get('mobile'),
                full_name = validated_data.get('full_name'),
                password = validated_data.get('password'),
                guest_id = generateGuestId(last_guest_id),
                address = validated_data.get("address"),
                email = validated_data.get("email")
            )
            return user
           
        else:
            FIRST_GUEST_ID = "LUX-001"
            user = User.objects.create_walkin_user(
                mobile = validated_data['mobile'],
                full_name = validated_data.get('full_name'),
                password = validated_data.get('password'),
                guest_id = FIRST_GUEST_ID
            )
            return user
    
    
class AdminRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=68, min_length=6, write_only=True)
    password2= serializers.CharField(max_length=68, min_length=6, write_only=True)

    class Meta:
        model=User
        fields = ['email', 'full_name', 'password', 'password2']

    def validate(self, attrs):
        password=attrs.get('password', '')
        password2 =attrs.get('password2', '')
        if password !=password2:
            raise serializers.ValidationError("passwords do not match")
         
        return attrs

    def create(self, validated_data):
        user= User.objects.create_adminuser(
            email = validated_data['email'],
            full_name = validated_data.get('full_name'),
            password = validated_data.get('password'),
            
            )
        return user


# class AdminRegisterSerializer(serializers.ModelSerializer):
#     password = serializers.CharField(max_length=68, min_length=6, write_only=True)
#     password2= serializers.CharField(max_length=68, min_length=6, write_only=True)

#     class Meta:
#         model=User
#         fields = ['email', 'full_name', 'password', 'password2']

#     def validate(self, attrs):
#         password=attrs.get('password', '')
#         password2 =attrs.get('password2', '')
#         if password !=password2:
#             raise serializers.ValidationError("passwords do not match")
         
#         return attrs

#     def create(self, validated_data):
#         user = User.objects.create_user(**validated_data)  # Assuming a create_user method
#         user.is_staff = True
#         user.is_superuser = True
#         user.save()
#         return user
    
    
class AdminLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255, required=True)
    password = serializers.CharField(max_length=128, write_only=True, required=True)
    is_staff = serializers.BooleanField(read_only=True)  # Added field for staff status

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if not email:
            raise serializers.ValidationError("Email is required")

        if not password:
            raise serializers.ValidationError("Password is required")

        user = authenticate(email=email, password=password)
        if not user or not user.is_staff:  # Use is_staff for admin privileges
            raise serializers.ValidationError("Invalid credentials or you are not an admin user")

        attrs['user'] = user
        return attrs
    
    
class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=155, min_length=6)
    password = serializers.CharField(max_length=68, write_only=True)
    full_name = serializers.CharField(max_length=255, read_only=True)
    access_token = serializers.CharField(max_length=255, read_only=True)
    refresh_token = serializers.CharField(max_length=255, read_only=True)
    is_staff = serializers.BooleanField(read_only=True)  # Added field for staff status

    class Meta:
        model = User
        fields = ['email', 'password', 'full_name', 'access_token', 'refresh_token', 'is_staff']

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        request = self.context.get('request')
        user = authenticate(request, email=email, password=password)
        if not user:
            raise AuthenticationFailed("Invalid credentials. Please try again.")
        
        # Check if the user is staff
        is_staff = user.is_staff

        tokens = user.tokens()
        return {
            'email': user.email,
            'full_name': user.get_full_name,
            "access_token": str(tokens.get('access')),
            "refresh_token": str(tokens.get('refresh')),
            "is_staff": is_staff,  # Include staff status in the response
        }
 
 
class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)

    class Meta:
        fields = ['email']

    def validate(self, attrs):
        
        email = attrs.get('email')
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            existing_otp = OneTimePassword.objects.get(user=user.id)
            if existing_otp:
                existing_otp.delete()
                
            send_generated_otp_to_email(email)

        return super().validate(attrs)
    
    
class SetNewPasswordSerializer(serializers.Serializer):
    password=serializers.CharField(max_length=100, min_length=6, write_only=True)
    confirm_password=serializers.CharField(max_length=100, min_length=6, write_only=True)
    token=serializers.CharField(min_length=4, write_only=True)

    class Meta:
        fields = ['password', 'confirm_password', 'token']

    def validate(self, attrs):
        try:
            token=attrs.get('token')
            password=attrs.get('password')
            confirm_password=attrs.get('confirm_password')
            
            #Get OTP Record
            otp = OneTimePassword.objects.get(otp=str(token))

            user=User.objects.get(id=otp.user.id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                raise AuthenticationFailed("reset link is invalid or has expired", 401)
            if password != confirm_password:
                raise AuthenticationFailed("passwords do not match")
            user.set_password(password)
            user.save()
            return user
        except Exception as e:
            return AuthenticationFailed("link is invalid or has expired")
    

# class SetNewPasswordSerializer(serializers.Serializer):
#     password=serializers.CharField(max_length=100, min_length=6, write_only=True)
#     confirm_password=serializers.CharField(max_length=100, min_length=6, write_only=True)
#     uidb64=serializers.CharField(min_length=1, write_only=True)
#     token=serializers.CharField(min_length=3, write_only=True)

#     class Meta:
#         fields = ['password', 'confirm_password', 'uidb64', 'token']

#     def validate(self, attrs):
#         try:
#             token=attrs.get('token')
#             uidb64=attrs.get('uidb64')
#             password=attrs.get('password')
#             confirm_password=attrs.get('confirm_password')

#             user_id=force_str(urlsafe_base64_decode(uidb64))
#             user=User.objects.get(id=user_id)
#             if not PasswordResetTokenGenerator().check_token(user, token):
#                 raise AuthenticationFailed("reset link is invalid or has expired", 401)
#             if password != confirm_password:
#                 raise AuthenticationFailed("passwords do not match")
#             user.set_password(password)
#             user.save()
#             return user
#         except Exception as e:
#             return AuthenticationFailed("link is invalid or has expired")
    
class LogoutUserSerializer(serializers.Serializer):
    refresh_token=serializers.CharField()

    # default_error_message = {
    #     'bad_token': ('Token is expired or invalid')
    # }

    def validate(self, attrs):
        self.token = attrs.get('refresh_token')

        return attrs

    def save(self, **kwargs):
        try:
            token=RefreshToken(self.token)
            token.blacklist()
        except TokenError:
            raise serializers.ValidationError("Token is Invalid")
           # return self.fail("")


#USER SERIALIZERS
class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model=User
        fields = ['id', 'guest_id', 'email', 'mobile', 'full_name', 'valid_address',  'valid_id', 'occupation', 'date_joined', 'is_mobile_verified', 'is_staff']
        
#VERIFICATION SERIALIZERS
class VerificationSerializer(serializers.ModelSerializer):
    #user = UserSerializer(many=False, read_only=True)
    
    class Meta:
        model=MobileVerification
        fields = [ 'email', 'msisdn', 'first_name', 'middle_name', 'last_name', 'address',  'gender', 'date_of_birth']