# tests/unit/test_event_replayer.py
import pytest
from src.sim.event_persistence import EventPersistence
from src.sim.event_replayer import EventReplayer
from src.scheduler.scheduler import SystemController

def test_replay_restores_system_pause(system, tmp_path):
    """테스트 1: Pause 이벤트가 새 시스템의 상태를 일시정지로 바꾸는지 확인"""
    system.pause()
    
    filepath = tmp_path / "events.json"
    EventPersistence.save(system.bus.get_history(), filepath)

    # 완전히 새로운 시스템 객체 생성
    new_system = SystemController() 
    events = EventPersistence.load(filepath)

    # 리플레이 실행
    EventReplayer.replay(new_system, events)

    assert new_system.is_paused() is True

def test_replay_applies_multiple_events(system, tmp_path):
    """테스트 2: 복합적인 이벤트 흐름(Pause -> Resume)이 정확히 반영되는지 확인"""
    system.pause()
    system.resume()

    filepath = tmp_path / "events.json"
    EventPersistence.save(system.bus.get_history(), filepath)

    new_system = SystemController()
    events = EventPersistence.load(filepath)

    EventReplayer.replay(new_system, events)

    # 최종 상태는 Resume이어야 함
    assert new_system.is_paused() is False