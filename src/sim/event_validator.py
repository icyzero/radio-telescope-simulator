# src/sim/event_validator.py
from src.sim.event_types import EventType

class EventValidator:
    # 🎯 Day 79: 필수 페이로드 규격 고도화
    REQUIRED_PAYLOAD = {
        EventType.COMMAND_STARTED: ["cmd_type"],
        EventType.COMMAND_SUCCESS: ["cmd_type", "result_state"], # result_state 강제
        EventType.COMMAND_FAILED: ["cmd_type", "reason", "result_state"],
        EventType.MANAGER_CRITICAL_STOP: ["reason"],
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

        # 3. 필수 키 검증
        required_keys = EventValidator.REQUIRED_PAYLOAD.get(event.type, [])
        for key in required_keys:
            if key not in event.payload:
                raise ValueError(
                    f"Missing required payload key '{key}' for {event.type}. "
                    f"Payload: {event.payload}"
                )

        # 4. [추가] SUCCESS와 FAILED 모두 result_state 구조 검증
        if event.type in [EventType.COMMAND_SUCCESS, EventType.COMMAND_FAILED]:
            result_state = event.payload.get("result_state")
            if not isinstance(result_state, dict):
                raise ValueError(f"result_state must be a dictionary for {event.type}")
            
            # 최소 기준 정의: manager_state와 queue_size 확인
            if "manager_state" not in result_state:
                raise ValueError("result_state must contain 'manager_state'")
            
        # 5. sim_time 검증 (물리적 시간의 가역성 방지)
        if event.sim_time < 0:
            raise ValueError(f"sim_time must be >= 0 (current: {event.sim_time})")

        # 6. [Day 76] Version 검증
        if not isinstance(event.version, int):
            raise ValueError(f"Event version must be int, but got {type(event.version)}")

        if event.version <= 0:
            raise ValueError(f"Event version must be >= 1 (current: {event.version})")

        return True