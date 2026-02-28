#tests/integration/test_system_recovery.py

import pytest
from src.controller.command import MoveCommand
from src.sim.event import EventType

def test_reset_only_allowed_when_locked(system):
    manager = system.managers["A"]
    
    # 1. NORMAL(IDLE) 상태에서 리셋 시도 -> 플래그 변화 없어야 함
    manager.reset_critical()
    assert manager._is_critical is False

    # 2. 강제로 LOCKED 상태 유도
    manager.add_command(MoveCommand(alt=10, az=10))
    system.update(0.1)
    manager.telescope.stop() 
    system.update(0.1)
    assert manager._is_critical is True # LOCKED 진입 확인

    # 3. LOCKED 상태에서 리셋 -> 성공해야 함
    manager.reset_critical()
    assert manager._is_critical is False

def test_reset_clears_critical_state_and_enables_new_commands(system):
    manager = system.managers["A"]
    
    # 1. 장애 발생 및 봉인
    manager.add_command(MoveCommand(alt=45, az=45))
    system.update(0.1)
    manager.telescope.stop()
    system.update(0.1)
    
    # 2. 리셋 수행
    manager.reset_critical()
    
    # 3. 새로운 명령 투입 테스트
    manager.add_command(MoveCommand(alt=20, az=20))
    system.update(0.1)
    
    # 🎯 검증: 리셋 후에는 새로운 명령이 STARTED 되어야 함
    started_events = [e for e in system.bus.get_events(EventType.COMMAND_STARTED) if e.source == "A"]
    assert len(started_events) == 2 # 장애 전 1번 + 리셋 후 1번

def test_reset_does_not_emit_duplicate_critical_events(system):
    manager = system.managers["A"]
    # 장애 유도
    manager.add_command(MoveCommand(alt=10, az=10))
    system.update(0.1)
    manager.telescope.stop()
    system.update(0.1)
    
    initial_critical_count = len(system.bus.get_events(EventType.MANAGER_CRITICAL_STOP))
    
    # 리셋 수행
    manager.reset_critical()
    system.update(0.1)
    
    # 🎯 검증: 리셋 후에도 CRITICAL_STOP 이벤트는 늘어나지 않아야 함
    assert len(system.bus.get_events(EventType.MANAGER_CRITICAL_STOP)) == initial_critical_count