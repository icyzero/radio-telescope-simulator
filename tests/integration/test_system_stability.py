# tests/integration/test_system_stability.py
import pytest
from src.controller.command import MoveCommand
from src.sim.event import EventType

def test_command_lifecycle_strict_order(system):
    manager = system.managers["A"]
    # 1. 명령 추가
    manager.add_command(MoveCommand(alt=10, az=10))

    # 2. 충분한 시간 업데이트 (도착할 때까지)
    for _ in range(50): system.update(0.1)

    # 3. 해당 매니저의 이벤트만 추출
    m_events = [e for e in system.bus.get_events() if e.source == "A"]
    types = [e.type for e in m_events]

    # 🎯 검증: 정확히 시작 후 성공 순서여야 하며, 중복이 없어야 함
    assert types == [
        EventType.COMMAND_STARTED,
        EventType.COMMAND_SUCCESS
    ]

def test_no_progress_while_paused(system):
    manager = system.managers["A"]
    
    # 1. 시스템 정지
    system.global_pause()
    
    # 2. 정지 상태에서 명령 추가
    manager.add_command(MoveCommand(alt=30, az=30))

    # 3. 시간 흐름 시뮬레이션
    for _ in range(10):
        system.update(0.1)

    # 🎯 검증: STARTED 이벤트가 발생하지 않아야 함 (진행 차단 보장)
    started_events = system.bus.get_events(EventType.COMMAND_STARTED)
    assert len(started_events) == 0
    
    # 4. 재개 후 확인
    system.global_resume()
    system.update(0.1)
    assert len(system.bus.get_events(EventType.COMMAND_STARTED)) == 1