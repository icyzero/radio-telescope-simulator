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
        
        # 2. 매니저 및 명령 결과 복원 (성공/실패 통합 처리)
        elif t in [EventType.COMMAND_SUCCESS, EventType.COMMAND_FAILED]:
            if event.source in system.managers:
                manager = system.managers[event.source]
                
                # [Day 79.5] 이제 실패(FAILED) 이벤트도 result_state를 반드시 가집니다.
                res = event.payload.get("result_state", {})
                
                # 🎯 기록된 '진실'을 주입 (더 이상 추측하지 않음)
                manager.state = res.get("manager_state", "IDLE")
                
                # 세부 상태(망원경 등)도 기록되어 있다면 복원
                if "telescope" in res:
                    tel_data = res["telescope"]
                    # if hasattr(manager.telescope, 'set_state'):
                    #     manager.telescope.set_state(tel_data)