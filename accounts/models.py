from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.forms import UUIDField
from django.utils.translation import gettext_lazy as _
from rest_framework_simplejwt.tokens import RefreshToken
import uuid

from accounts.managers import UserManager, VerificationManager
# Create your models here.

AUTH_PROVIDERS ={'email':'email', 'google':'google'}

class User(AbstractBaseUser, PermissionsMixin):
    #id = models.BigAutoField(primary_key=True, editable=False) 
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable = False, 
        unique=True)
    guest_id = models.CharField(max_length=10, verbose_name=_("Guest Id"), null=True, unique=True)
    email = models.EmailField(
        max_length=255, verbose_name=_("Email Address"), unique=True
    )
    mobile = models.CharField(max_length=11,
     verbose_name=_("Mobile Number"), unique=True, null=True, blank=False
    )
    full_name = models.CharField(max_length=100, verbose_name=_("Full Name"), null=True, blank=False)
    valid_address = models.CharField(max_length=255, verbose_name=_("Home Address"), null=True)
    valid_id = models.CharField(max_length=150, null=True)
    occupation = models.CharField(max_length=30, null=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_verified=models.BooleanField(default=False, null = True)
    is_mobile_verified=models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    date_created = models.DateTimeField(auto_now_add=True, null = True)
    last_login = models.DateTimeField(auto_now=True)
    auth_provider=models.CharField(max_length=50, blank=False, null=False, default=AUTH_PROVIDERS.get('email'))

    USERNAME_FIELD = "email"

    REQUIRED_FIELDS = ["full_name", "mobile"]

    objects = UserManager()

    def tokens(self):    
        refresh = RefreshToken.for_user(self)
        return {
            "refresh":str(refresh),
            "access":str(refresh.access_token)
        }
    

    def __str__(self):
        return self.email

    @property
    def get_full_name(self):
        return f"{self.full_name.title()}"
    
    def get_full_name(self):
        return f"{self.full_name}"
    
class OneTimePassword(models.Model):
    user=models.OneToOneField(User, on_delete=models.CASCADE)
    otp=models.CharField(max_length=6)

def __str__(self):
    return f"{self.user.full_name} - otp code"


class MobileVerification(models.Model):
    id = models.BigAutoField(primary_key=True, editable=False) 
    user = models.ForeignKey(User,on_delete=models.SET_NULL, null=True, blank=True)
    email = models.EmailField(
        max_length=255, verbose_name=_("Email Address"), null=True
    )
    msisdn = models.CharField(max_length=11,
     verbose_name=_("Mobile Number"), unique=True, null=True, blank=False
    )
    first_name = models.CharField(max_length=100, verbose_name=_("First Name"), null=True)
    middle_name = models.CharField(max_length=100, verbose_name=_("Middle Name"), null=True)
    last_name = models.CharField(max_length=100, verbose_name=_("Last Name"), null=True)
    gender = models.CharField(max_length=15, verbose_name=_("Gender"), null=True)
    date_of_birth = models.DateField(verbose_name=_("Date of Birth"), null=True)
    address = models.CharField(max_length=255, verbose_name=_("Home Address"), null=True)
    address_city = models.CharField(max_length=255, verbose_name=_("Address City"), null=True)
    address_state = models.CharField(max_length=255, verbose_name=_("Address State"), null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    objects = VerificationManager()

    def __str__(self):
        return f"{self.msisdn.title()} --> {self.first_name.title()} {self.last_name.title()}"

    @property
    def get_full_name(self):
        return f"{self.first_name.title()} {self.last_name.title()}"