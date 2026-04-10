# src/sim/event_types.py
from enum import Enum, auto

class EventType(Enum):
    # 시스템 제어 관련
    SYSTEM_PAUSED = auto()
    SYSTEM_RESUMED = auto()
    SYSTEM_STOPPED = auto()

    # 명령 라이프사이클 관련
    COMMAND_ADDED = auto()
    COMMAND_STARTED = auto()
    COMMAND_SUCCESS = auto()
    COMMAND_FAILED = auto()
    COMMAND_CANCELLED = auto()

    # 예외 상황
    INVALID_COMMAND = auto()
    MANAGER_CRITICAL_STOP = auto()
    
    #[day 96추가]
    CONFIG_CHANGED = auto() 