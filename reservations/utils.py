from datetime import date
from .enums import RoomStatus
from django.core.mail import send_mail
from django.template.loader import render_to_string
from backend import settings
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail



def format_room_allocation_records(records):
    for r in records:
                if r.status == 1:
                    r.status = RoomStatus(r.status).name
                elif r.status == 2:
                    r.status = RoomStatus(r.status).name
                elif r.status == 3:
                    r.status = RoomStatus(r.status).name
                elif r.status == 4:
                    r.status = RoomStatus(r.status).name
                elif r.status == 5:
                    r.status = RoomStatus(r.status).name
                    
    return records


def is_between(check_date, start_date, end_date):
    """
    Checks if a check_date is between start_date and end_date (inclusive).

    Args:
        check_date: The date to check.
        start_date: The start date of the range.
        end_date: The end date of the range.

    Returns:
        True if check_date is between start_date and end_date, False otherwise.
    """
    return start_date <= check_date <= end_date



def send_admin_notification(user_data, room_data, action):
    subject = f'User {action} Notification'
    from_email = settings.SENDGRID_SENDER_ID
    recipient_list = [settings.ADMIN_EMAIL]
    
    context = {
        'user_data': user_data,
        'room_data': room_data,
        'action': action,
    }
    
    message = render_to_string('action.html', context)
    
    SENDGRID_API_KEY = settings.SENDGRID_LIVE_KEY
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        mail = Mail(
            from_email=from_email,
            to_emails=recipient_list,
            subject=subject,
            html_content=message
        )
        response = sg.send(mail)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(str(e))