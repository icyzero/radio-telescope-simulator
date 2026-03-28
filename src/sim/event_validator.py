# src/sim/event_validator.py
from src.sim.event_types import EventType
from src.sim.event_schema import EventSchema

class EventValidator:
    @staticmethod
    def validate(event):
        """이벤트의 유효성을 검증 (버전별 하이브리드 방식)"""
        
        # 1. 기본 타입 및 물리 법칙 검증 (기존 로직 유지)
        if not isinstance(event.type, EventType):
            raise ValueError(f"Invalid event type: {event.type}")
        if not isinstance(event.payload, dict):
            raise ValueError(f"Payload must be dict")
        if event.sim_time < 0:
            raise ValueError(f"sim_time must be >= 0")

        # 2. [Day 82 핵심] 버전 추출 및 버전 타입 검증
        version = getattr(event, 'version', 1)
        if not isinstance(version, int) or version <= 0:
            raise ValueError(f"Event version must be int >= 1")

        # 3. [Day 82 핵심] EventSchema를 통한 버전별 필수 필드 검사
        # 이제 REQUIRED_PAYLOAD 딕셔너리 대신 Schema 매니저에게 물어봅니다.
        required_fields = EventSchema.get_required_fields(event.type, version)
        
        for field in required_fields:
            if field not in event.payload:
                raise ValueError(
                    f"[v{version}] Missing required field '{field}' for {event.type}. "
                    f"Payload: {event.payload}"
                )

        # 4. 세부 구조 검증 (필요 시 버전별로 분기 가능)
        # 예: v1, v2 모두 공통적으로 result_state가 있다면 여기서 추가 검사
        if "result_state" in event.payload:
            res = event.payload["result_state"]
            if not isinstance(res, dict) or "manager_state" not in res:
                raise ValueError(f"[v{version}] Invalid result_state structure")

        return True