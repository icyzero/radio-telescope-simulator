from enum import Enum

class TelescopeState(Enum):
    IDLE = "IDLE"
    MOVING = "MOVING"
    PARKED = "PARKED"
    ERROR = "ERROR"


class CommandType(Enum):
    MOVE = "MOVE"
    PARK = "PARK"
    STOP = "STOP"
