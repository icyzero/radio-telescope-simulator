# tests/unit/test_event_validator.py
import pytest
from src.sim.event import Event, EventType
from src.sim.event_validator import EventValidator

def test_invalid_event_type_should_be_rejected():
    """테스트 1: EventType이 아닌 잘못된 타입이 들어오면 거절"""
    fake_event = Event(type="INVALID_STRING", source="test", payload={})
    assert EventValidator.validate(fake_event) is False

def test_missing_payload_should_be_rejected():
    """테스트 2: 필수 payload 데이터(cmd_type)가 없으면 거절"""
    event = Event(
        type=EventType.COMMAND_STARTED,
        source="A",
        payload={} # 필수 키 'cmd_type' 누락
    )
    assert EventValidator.validate(event) is False

def test_valid_event_should_pass():
    """테스트 3: 규격에 맞는 이벤트는 정상 통과"""
    event = Event(
        type=EventType.COMMAND_STARTED,
        source="A",
        payload={"cmd_type": "MoveCommand"}
    )
    assert EventValidator.validate(event) is True