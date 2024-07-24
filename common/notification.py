from . import emailing
from . import sms
from asgiref.sync import sync_to_async
import asyncio

class Notification:
    @staticmethod
    async def send_email_async(to_email, subject, html_content):
        await sync_to_async(emailing.send_email_using_sendgrid)(to_email, subject, html_content)
    
    @staticmethod
    async def send_sms_async(recipient, message):
        await sync_to_async(sms.send_sms_using_sendcharm)(recipient, message)
