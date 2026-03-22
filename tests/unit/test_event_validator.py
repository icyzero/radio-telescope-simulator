# tests/unit/test_event_validator.py
import pytest
from src.sim.event import Event, EventBus
from src.sim.event_types import EventType # 경로 주의!
from src.sim.event_validator import EventValidator

def test_invalid_event_type_should_be_rejected():
    """테스트 1: EventType이 아닌 잘못된 타입이 들어오면 거절"""
    fake_event = Event(type="INVALID_STRING", source="test", payload={})
    # 이제 False 리턴을 기다리는 게 아니라, ValueError가 터지는지 확인합니다.
    with pytest.raises(ValueError) as excinfo:
        EventValidator.validate(fake_event)
    
    assert "Invalid event type" in str(excinfo.value)

def test_missing_payload_should_be_rejected():
    """테스트 2: 필수 payload 데이터(cmd_type)가 없으면 거절"""
    event = Event(
        type=EventType.COMMAND_STARTED,
        source="A",
        payload={} # 필수 키 'cmd_type' 누락
    )
    with pytest.raises(ValueError) as excinfo:
        EventValidator.validate(event)
    
    assert "Missing required payload key 'cmd_type'" in str(excinfo.value)

def test_valid_event_should_pass():
    """테스트 3: 규격에 맞는 이벤트는 정상 통과"""
    event = Event(
        type=EventType.COMMAND_STARTED,
        source="A",
        payload={"cmd_type": "MoveCommand"}
    )
    assert EventValidator.validate(event) is True
    
#day 75테스트
def test_bus_publish_should_raise_error_for_invalid_event():
    """테스트 2-1: EventBus에 잘못된 이벤트를 넣으면 즉시 ValueError가 터져야 함"""
    bus = EventBus()
    
    # 1. 필수 키(cmd_type)가 누락된 이벤트 생성
    invalid_event = Event(
        type=EventType.COMMAND_STARTED,
        source="Manager_A",
        payload={},  # 'cmd_type'이 빠짐
        sim_time=1.0
    )

    # 2. publish 시점에 예외가 발생하는지 검증
    with pytest.raises(ValueError) as excinfo:
        bus.publish(invalid_event)
    
    # 에러 메시지에 우리가 설정한 문구가 포함되었는지 확인
    assert "Missing required payload key 'cmd_type'" in str(excinfo.value)
    # Bus의 히스토리에 기록되지 않았는지 확인
    assert len(bus.get_events()) == 0

def test_bus_publish_should_raise_error_for_negative_sim_time():
    """테스트 2-2: sim_time이 음수이면 절대 기록되지 않아야 함"""
    bus = EventBus()
    
    negative_time_event = Event(
        type=EventType.SYSTEM_PAUSED,
        source="System",
        payload={},
        sim_time=-5.0  # 음수 시간
    )

    with pytest.raises(ValueError) as excinfo:
        bus.publish(negative_time_event)
    
    assert "sim_time must be >= 0" in str(excinfo.value)
    assert len(bus.get_events()) == 0

def test_bus_publish_should_pass_for_valid_event():
    """테스트 2-3: 정상적인 데이터는 기존처럼 잘 기록되어야 함 (회귀 테스트)"""
    bus = EventBus()
    
    valid_event = Event(
        type=EventType.COMMAND_STARTED,
        source="Manager_A",
        payload={"cmd_type": "MoveCommand"},
        sim_time=10.0
    )

    # 예외 없이 통과해야 함
    bus.publish(valid_event)
    
    assert len(bus.get_events()) == 1
    assert bus.get_events()[0].type == EventType.COMMAND_STARTED