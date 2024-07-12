from datetime import date
from .enums import RoomStatus

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