# src/sim/event_metrics.py
from src.sim.event import EventType

class EventMetrics:
    def __init__(self):
        self.command_started = 0
        self.command_success = 0
        self.command_failed = 0

    def handle(self, event):
        """이벤트 타입을 확인하여 통계 수치를 업데이트"""
        if event.type == EventType.COMMAND_STARTED:
            self.command_started += 1
        elif event.type == EventType.COMMAND_SUCCESS:
            self.command_success += 1
        elif event.type == EventType.COMMAND_FAILED:
            self.command_failed += 1

    @property
    def success_rate(self):
        """성공률 계산 (보너스 기능)"""
        if self.command_started == 0:
            return 0.0
        return (self.command_success / self.command_started) * 100