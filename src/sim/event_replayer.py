# src/sim/event_replayer.py
from src.sim.event_validator import EventValidator
from src.sim.event_types import EventType

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
        # Day 75에서 추가한 검증 로직
        if not EventValidator.validate(event):
            return
        
        t = event.type
        payload = event.payload

        # 1. 시스템 제어 복원
        if t == EventType.SYSTEM_PAUSED:
            system.mode = "PAUSED"
        elif t == EventType.SYSTEM_RESUMED:
            system.mode = "NORMAL"
        
        # 2. 매니저 및 명령 결과 복원 (핵심)
        elif t in [EventType.COMMAND_SUCCESS, EventType.COMMAND_FAILED]:
            if event.source in system.managers:
                manager = system.managers[event.source]
                # 명령이 끝났으므로 매니저를 IDLE 상태로 강제 전환
                manager.state = "IDLE" 
                # 만약 payload에 결과 좌표가 있다면 여기서 복원
                # if "final_pos" in payload:
                #     manager.telescope.set_position(payload["final_pos"])