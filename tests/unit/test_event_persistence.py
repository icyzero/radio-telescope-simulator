# tests/unit/test_event_persistence.py
import pytest
import json
from src.sim.event_persistence import EventPersistence
from src.controller.command import MoveCommand
from src.sim.event import Event

def test_event_persistence_creates_file(system, tmp_path):
    """테스트 1: 파일이 실제로 생성되는지 확인"""
    manager = system.managers["A"]
    manager.add_command(MoveCommand(alt=10, az=10))
    for _ in range(5): system.update(1.0)

    filepath = tmp_path / "events.json"
    EventPersistence.save(system.bus.get_history(), filepath)

    assert filepath.exists()

def test_event_persistence_contains_events(system, tmp_path):
    """테스트 2: 저장된 JSON 데이터가 올바른 내용을 담고 있는지 확인"""
    manager = system.managers["A"]
    manager.add_command(MoveCommand(alt=10, az=10))
    for _ in range(5): system.update(1.0)

    filepath = tmp_path / "events.json"
    EventPersistence.save(system.bus.get_history(), filepath)

    # 저장된 파일을 다시 읽어서 검증
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    event_types = [e["type"] for e in data]
    assert "COMMAND_STARTED" in event_types
    assert data[0]["source"] == "A"

def test_event_load_restores_events(system, tmp_path):
    """테스트 1: 저장 후 불러온 리스트가 비어있지 않은지 확인"""
    from src.sim.event_persistence import EventPersistence
    from src.controller.command import MoveCommand

    # 데이터 생성 및 저장
    manager = system.managers["A"]
    manager.add_command(MoveCommand(alt=10, az=10))
    for _ in range(5): system.update(1.0)
    
    filepath = tmp_path / "events.json"
    EventPersistence.save(system.bus.get_history(), filepath)

    # 불러오기 실행
    loaded = EventPersistence.load(filepath)

    assert len(loaded) > 0
    assert isinstance(loaded[0], Event) # 객체 타입이 올바른지 검증

def test_loaded_events_preserve_data(system, tmp_path):
    """테스트 2: 복원된 객체의 내부 데이터(Enum 등)가 원본과 일치하는지 확인"""
    from src.sim.event_persistence import EventPersistence
    from src.sim.event import EventType
    from src.controller.command import MoveCommand

    manager = system.managers["A"]
    manager.add_command(MoveCommand(alt=10, az=10))
    for _ in range(5): system.update(1.0)

    filepath = tmp_path / "events.json"
    EventPersistence.save(system.bus.get_history(), filepath)
    
    loaded = EventPersistence.load(filepath)
    types = [e.type for e in loaded]

    # 문자열이 아닌 EventType Enum 객체인지가 핵심!
    assert EventType.COMMAND_STARTED in types
    assert isinstance(types[0], EventType)