# src/sim/event_logger.py

class EventLogger:
    def __init__(self):
        self.logs = [] # 수신한 이벤트 객체들을 차곡차곡 쌓아둡니다.

    def handle(self, event):
        """EventBus가 이벤트를 발행할 때 호출할 콜백 함수"""
        # 이벤트를 문자열로 변환하여 기록하거나, 객체 그대로 보관합니다.
        log_entry = f"[{event.sim_time:.2f}s] {event.type.name} from {event.source}: {event.payload}"
        self.logs.append(log_entry)