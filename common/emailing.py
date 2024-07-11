from django.conf import settings
import environ
from pathlib import Path
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail 
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
from asgiref.sync import sync_to_async


env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False)
)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

environ.Env.read_env(BASE_DIR / '.env')

def send_email_using_sendgrid(to_email, subject, html_content):
    key = settings.SENDGRID_LIVE_KEY
    sender = settings.SENDGRID_SENDER_ID
    
    if key != None and sender != None and len(to_email) > 0:
        message = Mail(sender, to_email, subject, html_content)
        
        try:
            sg = SendGridAPIClient(key)
            # print(key, sender, to_email, subject, html_content)
            response = sg.send(message)
            print(response.status_code)
            print(response.body)
            print(response.headers)
            
        except Exception as e:
            print(e)
            