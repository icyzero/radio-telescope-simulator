# src/sim/event_replayer.py
from src.sim.event_validator import EventValidator

class EventReplayer:
    @staticmethod
    def apply_event(system, event):
        # [Day 74 신규 로직] 유효하지 않은 이벤트는 무시
        if not EventValidator.validate(event):
            # 실무에서는 여기서 경고 로그를 남기는 것이 좋습니다.
            return

    @staticmethod
    def apply_event(system, event):
        """단일 이벤트를 분석하여 시스템의 API 호출"""
        t = event.type.name
        
        if t == "SYSTEM_PAUSED":
            system.pause()
        elif t == "SYSTEM_RESUMED":
            system.resume()
        elif t == "SYSTEM_STOPPED":
            system.stop()
        # 향후 Manager의 상태나 Command 결과 등을 여기에 확장 가능합니다.