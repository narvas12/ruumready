from django.conf import settings
import requests
import json

#Declare constsnts
DOJAH_APP_ID=settings.DOJAH_APP_ID
DOJAH_APP_KEY=settings.DOJAH_APP_KEY
DOJAH_BASEURL=settings.DOJAH_BASEURL

def get_verified_userdetails_by_phone(phone_number):
    url = f"{str(DOJAH_BASEURL)}api/v1/kyc/phone_number/basic?phone_number={phone_number}"
    
    # Add headers if needed
    headers = {
        'AppId': str(DOJAH_APP_ID),
        'Authorization': str(DOJAH_APP_KEY)
    }  

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for non-200 status codes

        # Process JSON data
        if response.headers.get('Content-Type') == 'application/json':
            data = response.json()
            return data.get("entity")
           
        else:
            json_data = json.loads(response.text)
            return json_data.get("entity")
            # Process non-JSON data (e.g., text, XML)
    
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")