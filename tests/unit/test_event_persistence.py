# tests/unit/test_event_persistence.py
import pytest
import json
from src.sim.event_persistence import EventPersistence
from src.controller.command import MoveCommand

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