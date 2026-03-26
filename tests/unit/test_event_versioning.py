# tests/unit/test_event_versioning.py

import pytest
from src.sim.event import Event
from src.sim.event_types import EventType
from src.sim.event_validator import EventValidator

def test_event_has_default_version_1():
    """테스트 1: 별도 설정 없어도 버전은 1이어야 함"""
    event = Event(type=EventType.SYSTEM_PAUSED, source="System")
    assert event.version == 1

def test_validator_should_reject_invalid_version_type():
    """테스트 2: 버전이 숫자가 아니면 거절"""
    event = Event(type=EventType.SYSTEM_PAUSED, source="System", version="v1")
    with pytest.raises(ValueError) as excinfo:
        EventValidator.validate(event)
    assert "Event version must be int" in str(excinfo.value)

def test_validator_should_reject_zero_or_negative_version():
    """테스트 3: 버전이 0 이하면 거절"""
    event = Event(type=EventType.SYSTEM_PAUSED, source="System", version=0)
    with pytest.raises(ValueError) as excinfo:
        EventValidator.validate(event)
    assert "Event version must be >= 1" in str(excinfo.value)

def test_replayer_should_fail_for_unknown_future_version():
    """테스트 4: 리플레이 엔진이 듣도 보도 못한 버전(예: 99)을 만나면 에러를 내야 함"""
    from src.sim.event_replayer import EventReplayer
    from src.scheduler.scheduler import SystemController

    sys = SystemController()
    # Validator는 통과하지만(정수 1 이상이므로), Replayer는 처리법을 모르는 상황
    future_event = Event(type=EventType.SYSTEM_PAUSED, source="System", version=99)
    
    with pytest.raises(ValueError) as excinfo:
        EventReplayer.apply_event(sys, future_event)
    assert "지원하지 않는 이벤트 버전" in str(excinfo.value)