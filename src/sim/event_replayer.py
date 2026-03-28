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
        
        # 버전별 '통역사' 연결
        if event.version == 1:
            EventReplayer._handle_v1(system, event)
        elif event.version == 2:
            # 미래에 v2 구현 시 여기에 추가
            pass
        else:
            raise ValueError(f"지원하지 않는 이벤트 버전입니다: {event.version}")
        system.last_processed_id = event.id

    @staticmethod
    def _handle_v1(system, event):
        """버전 1 전용 리플레이 로직 (기존 본문)"""
        t = event.type
        
        # 1. 시스템 제어 복원
        if t == EventType.SYSTEM_PAUSED:
            system.mode = "PAUSED"
        elif t == EventType.SYSTEM_RESUMED:
            system.mode = "NORMAL"
        
        # 2. 매니저 및 명령 결과 복원 (성공/실패 통합 처리)
        elif t in [EventType.COMMAND_SUCCESS, EventType.COMMAND_FAILED]:
            if event.source in system.managers:
                manager = system.managers[event.source]
                res = event.payload.get("result_state", {})
                
                # 기록된 '진실'을 주입
                manager.state = res.get("manager_state", "IDLE")
                
                # 세부 상태(망원경 등) 복원
                if "telescope" in res:
                    tel_data = res["telescope"]
                    # if hasattr(manager.telescope, 'set_state'):
                    #     manager.telescope.set_state(tel_data)