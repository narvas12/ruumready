from django.core.mail import EmailMessage
import random
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.apps import apps

def send_generated_otp_to_email(email): 
    #Assigning respective models
    OneTimePassword = apps.get_model('accounts.OneTimePassword')
    User = apps.get_model('accounts.User')
    
    otp=random.randint(1000, 9999) 
    user = User.objects.get(email=email)

    otp_obj=OneTimePassword.objects.create(user=user, otp=otp)
    #send the email 
    html_content = f"Hi {user.full_name} use the link below to reset your password {otp}"
    email_subject = "Reset your Password"
    sms_msg = html_content
        
    # notification.Notification.send_email_async(to_email=email, subject=email_subject, html_content=html_content)
    # notification.Notification.send_sms_async(recipient=mobile, message=sms_msg)


def send_generated_otp_to_email1(email, request): 
    #Assigning respective models
    OneTimePassword = apps.get_model('accounts.OneTimePassword')
    User = apps.get_model('accounts.User')
    
    subject = "One time passcode for Email verification"
    otp=random.randint(1000, 9999) 
    current_site=get_current_site(request).domain
    user = User.objects.get(email=email)
    email_body=f"Hi {user.full_name} thanks for signing up on {current_site} please verify your email with the \n one time passcode {otp}"
    from_email=settings.EMAIL_HOST
    otp_obj=OneTimePassword.objects.create(user=user, otp=otp)
    #send the email 
    d_email=EmailMessage(subject=subject, body=email_body, from_email=from_email, to=[user.email])
    d_email.send()


def send_normal_email(data):
    email=EmailMessage(
        subject=data['email_subject'],
        body=data['email_body'],
        from_email=settings.EMAIL_HOST_USER,
        to=[data['to_email']]
    )
    email.send()
    
    
def generateGuestId(lastUsedGuestId):
    guest_id_prefix = str(settings.GUEST_ID_PREFIX)
    newGuestId = str()
    if lastUsedGuestId:
        increment_value = 1
        splitGuestId = str(lastUsedGuestId).split("-")
        digit_part = int(splitGuestId[1]) + increment_value
        formatted_digit_part = "{:03d}".format(digit_part)
        newGuestId = f"{guest_id_prefix}{formatted_digit_part}"
    elif lastUsedGuestId == "":
        initValue = str(settings.GUEST_ID_INIT_VALUE)
        newGuestId = f"{guest_id_prefix}{initValue}"
    print(newGuestId)
    return newGuestId