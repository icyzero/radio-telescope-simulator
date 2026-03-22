# src/sim/event_validator.py
from src.sim.event import EventType

class EventValidator:
    # 각 이벤트 타입별로 반드시 존재해야 하는 payload 키 정의
    REQUIRED_PAYLOAD = {
        EventType.COMMAND_STARTED: ["cmd_type"],
        EventType.COMMAND_FAILED: ["reason"],
        EventType.MANAGER_CRITICAL_STOP: ["reason"],
        # SUCCESS처럼 추가 데이터가 필요 없는 경우는 빈 리스트
        EventType.COMMAND_SUCCESS: [],
    }

    @staticmethod
    def validate(event):
        """이벤트가 시스템에 적용 가능한 유효한 규격인지 검증"""
        # 1. 타입 검증: EventType 열거형 객체인지 확인
        if not isinstance(event.type, EventType):
            return False

        # 2. Payload 검증: 필수 키(Key)가 누락되었는지 확인
        required_keys = EventValidator.REQUIRED_PAYLOAD.get(event.type, [])
        for key in required_keys:
            if key not in event.payload:
                return False

        return True