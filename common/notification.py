from . import emailing
from . import sms
from asgiref.sync import sync_to_async
import asyncio

class Notification():
    
    def send_email_async(to_email, subject, html_content):
        emailing.send_email_using_sendgrid(to_email, subject, html_content)
    
    def send_sms_async(recipient, message):
        sms.send_sms_using_sendcharm(recipient, message)