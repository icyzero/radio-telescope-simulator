# src/sim/event_validator.py
from src.sim.event_types import EventType

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
        """이벤트의 유효성을 검증하며, 실패 시 즉시 예외 발생"""
        
        # 1. 타입 검증: Enum 객체인지 확인
        if not isinstance(event.type, EventType):
            raise ValueError(f"Invalid event type: {event.type}")

        # 2. Payload 타입 검증
        if not isinstance(event.payload, dict):
            raise ValueError(f"Payload must be dict, but got {type(event.payload)}")

        # 3. 필수 키 검증 (스키마 v1.0 준수)
        required_keys = EventValidator.REQUIRED_PAYLOAD.get(event.type, [])
        for key in required_keys:
            if key not in event.payload:
                raise ValueError(
                    f"Missing required payload key '{key}' for {event.type}"
                )

        # 4. sim_time 검증 (물리적 시간의 가역성 방지)
        if event.sim_time < 0:
            raise ValueError(f"sim_time must be >= 0 (current: {event.sim_time})")

        # 5. [Day 76] Version 검증
        if not isinstance(event.version, int):
            raise ValueError(f"Event version must be int, but got {type(event.version)}")

        if event.version <= 0:
            raise ValueError(f"Event version must be >= 1 (current: {event.version})")

        return True