# tests/unit/test_event_reliability.py
import pytest
import time
from src.sim.event import Event, EventType
from datetime import timedelta, datetime

def test_event_is_immutable():
    """Event 객체는 생성 후 수정이 불가능해야 함 (frozen=True 검증)"""
    event = Event(EventType.SYSTEM_PAUSED, source="SystemController")

    # frozen=True 속성 때문에 값을 변경하려고 하면 FrozenInstanceError 발생
    with pytest.raises(Exception):
        event.source = "Hacker_Source"

def test_event_string_representation():
    """Event 객체의 문자열 출력이 형식을 지키고 있는지 확인"""
    event = Event(
        type=EventType.SYSTEM_PAUSED, 
        source="System", 
        payload={"reason": "test"},
        sim_time=1.234
    )
    output = str(event)
    
    assert "[sim:1.234]" in output
    assert "System -> SYSTEM_PAUSED" in output
    assert "{'reason': 'test'}" in output

def test_event_timing_analysis(system):
    # 1. 이벤트 두 개 발행 (약간의 시차)
    system.bus.publish(Event(EventType.COMMAND_STARTED, "Manager_A"))
    time.sleep(0.01) # 아주 짧은 실제 시간 지연
    system.bus.publish(Event(EventType.COMMAND_SUCCESS, "Manager_A"))

    # 2. 히스토리에서 시간차 계산
    history = system.bus.get_history()
    start_time = history[0].timestamp
    end_time = history[1].timestamp

    # 3. 검증: 종료 시간이 시작 시간보다 이후인가?
    assert end_time > start_time
    assert (end_time - start_time) >= timedelta(seconds=0.01)

def test_event_has_timestamp():
    """이벤트 생성 시 자동으로 타임스탬프가 찍혀야 함"""
    event = Event(EventType.SYSTEM_PAUSED, "SYSTEM")
    assert event.timestamp is not None
    assert isinstance(event.timestamp, datetime)

def test_event_history_isolation(system):
    """get_history()가 원본 리스트를 변조하지 못하도록 복사본을 주는지 확인"""
    system.bus.publish(Event(EventType.SYSTEM_PAUSED, "SYSTEM"))
    
    history = system.bus.get_history()
    history.clear() # 가져온 리스트를 비워봄
    
    # 원본은 그대로 유지되어야 함
    assert len(system.bus.get_history()) == 1