from datetime import date

from backend import settings
from .enums import RoomStatus
from django.core.mail import send_mail
from django.template.loader import render_to_string



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



def send_check_in_email(user, bookings):
    subject = "Room Check-In Confirmation"
    admin_email = settings.ADMIN_EMAIL  


    user_message = render_to_string('emails/user_check_in.html', {
        'user': user,
        'bookings': bookings,
        'site_name': "LUXEVILLE",
    })
    send_mail(
        subject,
        user_message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )


    admin_message = render_to_string('emails/admin_check_in.html', {
        'user': user,
        'bookings': bookings,
        'site_name': "LUXEVILLE",
    })
    send_mail(
        subject,
        admin_message,
        settings.DEFAULT_FROM_EMAIL,
        [admin_email],
        fail_silently=False,
    )