# tests/unit/test_payload_completeness.py

import pytest
from src.sim.event import Event
from src.sim.event_types import EventType
from src.sim.event_validator import EventValidator

def test_command_success_requires_result_state():
    """테스트 1: COMMAND_SUCCESS에 result_state가 없으면 발행 실패해야 함"""
    invalid_event = Event(
        type=EventType.COMMAND_SUCCESS,
        source="Manager_A",
        payload={"cmd_type": "MOVE"}, # result_state 누락
        sim_time=1.0
    )

    with pytest.raises(ValueError) as excinfo:
        EventValidator.validate(invalid_event)
    
    assert "Missing required payload key 'result_state'" in str(excinfo.value)

def test_command_success_with_valid_payload():
    """테스트 2: 모든 정보가 포함된 이벤트는 정상 통과"""
    valid_event = Event(
        type=EventType.COMMAND_SUCCESS,
        source="Manager_A",
        payload={
            "cmd_type": "MOVE",
            "result_state": {"manager_state": "IDLE", "pos": (120, 45)}
        },
        sim_time=1.0
    )
    
    assert EventValidator.validate(valid_event) is True

def test_command_failed_requires_result_state():
    """테스트 3: COMMAND_FAILED에 result_state가 없으면 발행 실패해야 함"""
    invalid_failed_event = Event(
        type=EventType.COMMAND_FAILED,
        source="Manager_B",
        payload={
            "cmd_type": "TRACK",
            "reason": "Hardware Timeout"
            # result_state 누락!
        },
        sim_time=5.5
    )

    with pytest.raises(ValueError) as excinfo:
        EventValidator.validate(invalid_failed_event)
    
    assert "Missing required payload key 'result_state'" in str(excinfo.value)