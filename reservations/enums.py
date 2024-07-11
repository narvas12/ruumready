from enum import Enum, EnumMeta

class RoomStatus(Enum):
    AVAILABLE = 1
    UNAVAILABLE = 2
    BOOKED = 3
    CHECKED_IN = 4
    CHECKED_OUT = 5
    
    @classmethod
    def get_key_by_value(cls, value):
        for name, member in cls.__members__.items():
            if member.value == value:
                return name
        raise ValueError("Invalid value for status")
    
    @classmethod
    def enum_has_value(cls, value):
        for name, member in cls.__members__.items():
            if member.value == value:
                return True
           
        return False
    