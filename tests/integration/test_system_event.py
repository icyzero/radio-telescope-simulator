import pytest
from src.controller.command import MoveCommand
from src.sim.event import EventType

def test_should_record_pause_resume_sequence(system):
    system.global_pause()
    system.global_resume()
    
    # 💡 system.events 대신 system.bus.get_events() 사용
    all_events = system.bus.get_events()
    event_types = [e.type for e in all_events]
    
    # 💡 이제 문자열 "SYSTEM_PAUSED"가 아니라 EventType.SYSTEM_PAUSED 상수와 비교
    assert EventType.SYSTEM_PAUSED in event_types
    assert EventType.SYSTEM_RESUMED in event_types
    assert event_types.index(EventType.SYSTEM_PAUSED) < event_types.index(EventType.SYSTEM_RESUMED)

def test_command_lifecycle_events(system):
    manager = system.managers["A"]
    manager.add_command(MoveCommand(alt=10, az=10))
    for _ in range(20): system.update(0.1)
    
    # 💡 버스를 통해 이벤트 획득
    m_events = [e for e in system.bus.get_events() if e.source == "A"]
    types = [e.type for e in m_events]
    
    assert EventType.COMMAND_STARTED in types
    assert EventType.COMMAND_SUCCESS in types

def test_should_record_failure_when_telescope_stops_unexpectedly(system):
    manager = system.managers["A"]
    tele = manager.telescope
    
    # 1. 이동 명령 추가
    manager.add_command(MoveCommand(alt=45, az=45))
    system.update(0.1) # 실행 시작
    
    # 2. 강제로 하드웨어(망원경)를 STOPPED 상태로 만듦 (비정상 상황 시뮬레이션)
    tele.stop()
    system.update(0.1) # 매니저가 이를 감지하는 틱
    
    # 3. 이벤트 검증
    failed_events = system.bus.get_events(EventType.COMMAND_FAILED)
    critical_events = system.bus.get_events(EventType.MANAGER_CRITICAL_STOP)
    
    assert len(failed_events) > 0
    assert critical_events[0].payload["reason"] == "STOPPED"