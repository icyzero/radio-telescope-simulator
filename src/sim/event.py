#src/sim/event.py

from dataclasses import dataclass, field
from datetime import datetime
from src.sim.event_types import EventType
from src.utils.logger import log

@dataclass(frozen=True)
class Event:
    type: EventType           # 예: "SYSTEM_PAUSED", "COMMAND_SUCCESS"
    source: str         # 예: "SystemController", "Manager_A"
    payload: dict = field(default_factory=dict)
    sim_time: float = 0.0  # 시뮬레이션 내부 경과 시간
    timestamp: datetime = field(default_factory=datetime.now) # 실제 기록 시간
    version: int = 1 # [Day 76] 데이터 규격 버전 관리 (기본값 1)
    id: int = 0

    def __str__(self):
        return (
        f"[{self.id:04d}] "
        f"[sim:{self.sim_time:.3f}] "
        f"[{self.timestamp.strftime('%H:%M:%S')}] "
        f"{self.source} -> {self.type.name} "
        f"{self.payload}"
        )

    @property
    def wall_time(self):
        """timestamp의 별칭 (실제 기록 시각)"""
        return self.timestamp
    
# 관측을 위한 전담 로거 함수
def event_pretty_logger(event: Event):
    # 콘솔에 사람이 읽기 좋은 형태로 출력
    log(str(event))