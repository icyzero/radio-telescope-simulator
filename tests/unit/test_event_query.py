# tests/unit/test_event_query.py
import pytest
from src.sim.event import EventType
from src.controller.command import MoveCommand

def test_query_by_event_type(system):
    manager = system.managers["A"]
    manager.add_command(MoveCommand(alt=10, az=10))
    for _ in range(10): system.update(1.0)

    # SUCCESS 타입만 골라내기
    events = system.bus.get_events(type=EventType.COMMAND_SUCCESS)
    assert len(events) == 1
    assert events[0].type == EventType.COMMAND_SUCCESS

def test_query_by_source(system):
    manager = system.managers["A"]
    manager.add_command(MoveCommand(alt=10, az=10))
    for _ in range(10): system.update(1.0)

    # 출처(A)가 명확한 이벤트만 골라내기
    events = system.bus.get_events(source="A") # Manager_A 대신 "A" (등록된 이름 기준)
    assert len(events) > 0
    assert all(e.source == "A" for e in events)

def test_query_combined_filters(system):
    """복합 필터링 테스트: 특정 시간대에 발생한 특정 타입 찾기"""
    manager = system.managers["A"]
    manager.add_command(MoveCommand(alt=10, az=10))
    for _ in range(10): system.update(1.0)

    # 0초에서 5초 사이에 발생한 STARTED 이벤트만 조회
    events = system.bus.get_events(
        type=EventType.COMMAND_STARTED,
        start_time=0.0,
        end_time=5.0
    )
    assert len(events) == 1