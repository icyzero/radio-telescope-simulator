#src/sim/event.py

from enum import Enum, auto
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
import time

class EventType(Enum):
    # 시스템 제어 관련
    SYSTEM_PAUSED = auto()
    SYSTEM_RESUMED = auto()
    SYSTEM_STOPPED = auto()
    
    # 명령 라이프사이클 관련
    COMMAND_STARTED = auto()
    COMMAND_SUCCESS = auto()
    COMMAND_FAILED = auto()
    COMMAND_CANCELLED = auto()
    
    # 예외 상황
    INVALID_COMMAND = auto()
    MANAGER_CRITICAL_STOP = auto()

@dataclass(frozen=True)
class Event:
    type: EventType           # 예: "SYSTEM_PAUSED", "COMMAND_SUCCESS"
    source: str         # 예: "SystemController", "Manager_A"
    payload: dict = field(default_factory=dict)
    sim_time: float = 0.0  # 시뮬레이션 내부 경과 시간
    timestamp: datetime = field(default_factory=datetime.now) # 실제 기록 시간

    def __str__(self):
        return (
        f"[sim:{self.sim_time:.3f}] "
        f"[{self.timestamp.strftime('%H:%M:%S')}] "
        f"{self.source} -> {self.type.name} "
        f"{self.payload}"
        )
    
# 관측을 위한 전담 로거 함수
def event_pretty_logger(event: Event):
    # 콘솔에 사람이 읽기 좋은 형태로 출력
    print(event)
    
class EventBus:
    def __init__(self):
        self._events: List[Event] = []

    def publish(self, event: Event):
        self._events.append(event)
        # 나중에 여기에 실시간 로그 출력이나 파일 저장을 붙일 수 있습니다.

    def get_events(self, event_type: Optional[EventType] = None) -> List[Event]:
        if event_type:
            return [e for e in self._events if e.type == event_type]
        return self._events.copy()

    def clear(self):
        self._events.clear()