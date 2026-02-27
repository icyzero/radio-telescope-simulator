# tests/integration/test_system_safety.py
import pytest
from src.controller.command import MoveCommand
from src.sim.event import EventType

def test_manager_critical_stop_blocks_new_commands(system):
    manager = system.managers["A"]
    tele = manager.telescope

    # 1. 첫 번째 명령 수행 중 장애 발생
    manager.add_command(MoveCommand(alt=45, az=45))
    system.update(0.1) # STARTED 발생
    
    tele.stop()        # 하드웨어 돌발 정지
    system.update(0.1) # CRITICAL_STOP 발생 및 락 활성화
    
    # 2. 락이 걸린 상태에서 새로운 명령 추가 시도
    manager.add_command(MoveCommand(alt=10, az=10))
    system.update(1.0) # 충분한 시간 흐름
    
    # 3. 검증
    all_events = system.bus.get_events()
    started_events = [e for e in all_events if e.type == EventType.COMMAND_STARTED]
    invalid_events = [e for e in all_events if e.type == EventType.INVALID_COMMAND]
    
    # 🎯 핵심 검증: 두 번째 명령은 절대로 시작되지 않았어야 함
    assert len(started_events) == 1 
    # 🎯 핵심 검증: 거절된 이유가 기록되어야 함
    assert len(invalid_events) >= 1

def test_manager_lock_integrity(system):
    manager = system.managers["A"]
    manager.add_command(MoveCommand(alt=45, az=45)) # 1번 명령
    manager.add_command(MoveCommand(alt=10, az=10)) # 2번 명령 (큐 대기)
    
    system.update(0.1) # 실행 시작
    manager.telescope.stop() # 장애 발생
    system.update(0.1) # 장애 감지 및 락
    
    # 🎯 검증 1: 락 상태 확인
    assert manager._is_critical is True
    
    # 🎯 검증 2: 자원 회수 확인 (현재 명령과 대기 큐 모두 비워져야 함)
    assert manager.current is None
    assert len(manager.queue) == 0
    
    # 🎯 검증 3: 락 상태에서 추가 시도 시 큐에 쌓이지 않는가?
    manager.add_command(MoveCommand(alt=90, az=90))
    assert len(manager.queue) == 0

def test_critical_event_should_be_emitted_exactly_once(system):
    manager = system.managers["A"]
    manager.add_command(MoveCommand(alt=45, az=45))
    system.update(0.1)
    
    manager.telescope.stop() # 장애 발생
    
    # 장애 감지 후 여러 번의 update 루프 가동
    for _ in range(5):
        system.update(0.1)
        
    # 🎯 검증: CRITICAL_STOP 이벤트는 전체 타임라인에서 딱 1번이어야 함
    critical_events = [
        e for e in system.bus.get_events() 
        if e.type == EventType.MANAGER_CRITICAL_STOP
    ]
    
    assert len(critical_events) == 1