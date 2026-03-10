# tests/unit/test_event_logger.py
import pytest
from src.sim.event_logger import EventLogger
from src.sim.event import EventType
from src.controller.command import MoveCommand

def test_event_logger_records_lifecycle(system):
    # 1. 독립적인 로거 생성 및 특정 이벤트 구독
    test_logger = EventLogger()
    system.bus.subscribe(EventType.COMMAND_STARTED, test_logger.handle)
    system.bus.subscribe(EventType.COMMAND_SUCCESS, test_logger.handle)

    # 2. 명령 실행
    manager_a = system.managers.get("A")
    manager_a.add_command(MoveCommand(alt=10, az=10))
    
    # 3. 시스템 업데이트 (실행 완료까지 충분히)
    for _ in range(5):
        system.update(1.0)

    # 4. 검증: 로거에 이벤트가 잘 쌓였는가?
    assert len(test_logger.logs) >= 2
    assert "COMMAND_STARTED" in test_logger.logs[0]
    assert "COMMAND_SUCCESS" in test_logger.logs[-1]