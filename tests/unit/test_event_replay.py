# tests/unit/test_event_replay.py
import pytest
from src.sim.event_replay import EventReplay
from src.sim.event import EventType
from src.controller.command import MoveCommand

def test_replay_preserves_event_order(system):
    """테스트 1: 원본 히스토리와 리플레이 순서가 일치하는지 확인"""
    manager = system.managers["A"]
    manager.add_command(MoveCommand(alt=10, az=10))

    for _ in range(5): 
        system.update(1.0)

    history = system.bus.get_history()
    replayer = EventReplay(history)

    # 제너레이터로부터 리스트를 생성하여 비교
    replayed_events = list(replayer.replay())

    assert replayed_events == history
    assert replayed_events[0].sim_time <= replayed_events[-1].sim_time

def test_replay_contains_command_events(system):
    """테스트 2: 리플레이되는 이벤트 내에 주요 생명주기 이벤트가 포함되었는지 확인"""
    manager = system.managers["A"]
    manager.add_command(MoveCommand(alt=10, az=10))

    for _ in range(5): 
        system.update(1.0)

    replayer = EventReplay(system.bus.get_history())
    event_types = [e.type for e in replayer.replay()]

    assert EventType.COMMAND_STARTED in event_types
    assert EventType.COMMAND_SUCCESS in event_types