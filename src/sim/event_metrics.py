# src/sim/event_metrics.py
from src.sim.event import EventType

class EventMetrics:
    def __init__(self):
        # 내부 카운터
        self.command_started = 0
        self.command_success = 0
        self.command_failed = 0

    def handle(self, event):
        if event.type == EventType.COMMAND_STARTED:
            self.command_started += 1
        elif event.type == EventType.COMMAND_SUCCESS:
            self.command_success += 1
        elif event.type == EventType.COMMAND_FAILED:
            self.command_failed += 1

    # 💡 get_diagnostics가 사용하는 이름으로 연결 (Alias)
    @property
    def total_commands(self):
        return self.command_started

    @property
    def failed_count(self):
        return self.command_failed

    @property
    def success_rate(self):
        if self.command_started == 0:
            return 0.0
        return (self.command_success / self.command_started) * 100