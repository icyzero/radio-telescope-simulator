#src/sim/event.py

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from src.sim.event_types import EventType
import time

@dataclass(frozen=True)
class Event:
    type: EventType           # 예: "SYSTEM_PAUSED", "COMMAND_SUCCESS"
    source: str         # 예: "SystemController", "Manager_A"
    payload: dict = field(default_factory=dict)
    sim_time: float = 0.0  # 시뮬레이션 내부 경과 시간
    timestamp: datetime = field(default_factory=datetime.now) # 실제 기록 시간
    version: int = 1 # [Day 76] 데이터 규격 버전 관리 (기본값 1)

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
        self._subscribers = {}

    def publish(self, event: Event):
        """이벤트를 발행하기 전 반드시 검증을 통과해야 함"""
        # 🔥 강제 정책 적용: 검증 실패 시 여기서 즉시 프로그램 중단(Exception)
        # 순환 참조 방지를 위해 함수 내부에서 임포트 (Local Import)
        from src.sim.event_validator import EventValidator
        EventValidator.validate(event)

        self._events.append(event)
        # 나중에 여기에 실시간 로그 출력이나 파일 저장을 붙일 수 있습니다.

    def get_events(self, event_type: Optional[EventType] = None) -> List[Event]:
        if event_type:
            return [e for e in self._events if e.type == event_type]
        return self._events.copy()

    def clear(self):
        self._events.clear()