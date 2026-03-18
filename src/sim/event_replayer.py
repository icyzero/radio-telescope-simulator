# src/sim/event_replayer.py

class EventReplayer:
    @staticmethod
    def replay(system, events):
        """이벤트 리스트를 순회하며 시스템 상태를 복원"""
        # 시간 순 정렬 보장
        sorted_events = sorted(events, key=lambda e: e.sim_time)
        for e in sorted_events:
            EventReplayer.apply_event(system, e)

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