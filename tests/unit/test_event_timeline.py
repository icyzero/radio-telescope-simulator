import pytest
from src.sim.event_timeline import EventTimeline
from src.sim.event import EventType
from src.controller.command import MoveCommand

def test_timeline_orders_events(system):
    """테스트 1: 이벤트 타입이 시간 순서대로 정렬되는지 확인"""
    manager = system.managers["A"]
    manager.add_command(MoveCommand(alt=10, az=10))

    for _ in range(10):
        system.update(1.0)

    timeline = EventTimeline(system.bus.get_history())
    types = timeline.get_types()

    # 첫 번째 이벤트는 반드시 STARTED여야 하고, 
    # SUCCESS는 그 뒤에 나타나야 합니다.
    assert types[0] == EventType.COMMAND_STARTED
    assert EventType.COMMAND_SUCCESS in types

def test_command_execution_duration(system):
    """테스트 2: 시작과 종료 사이의 소요 시간이 올바르게 계산되는지 확인"""
    manager = system.managers["A"]
    manager.add_command(MoveCommand(alt=10, az=10))

    for _ in range(10):
        system.update(1.0)

    timeline = EventTimeline(system.bus.get_history())
    duration = timeline.duration_between(
        EventType.COMMAND_STARTED,
        EventType.COMMAND_SUCCESS
    )

    # 소요 시간이 계산되어야 하며, 0초 이상이어야 함
    assert duration is not None
    assert duration >= 0