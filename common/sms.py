import json
from django.conf import settings
import environ
from pathlib import Path
import requests
from asgiref.sync import sync_to_async

def send_sms_using_sendcharm(recipient, message):
    url = settings.SENDCHAMP_BASEURL
    key = settings.SENDCHAMP_KEY
    sender = settings.SENDCHAMP_SENDER_ID
    route_type = "non_dnd"
    recipient = f"+234{recipient}"
    
    payload = {
        "to": recipient,
        "message": message,
        "sender_name": sender,
        "route": route_type
    }

    payload_to_json = json.dumps(payload).encode("utf-8")

    headers = {
        "Accept": "application/json,text/plain,*/*",
        "Content-Type": "application/json",
        'Authorization': f'Bearer {key}',
    }

    response = requests.request("POST", url, headers=headers, data=payload_to_json)

    print(response.text)