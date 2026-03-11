# tests/unit/test_event_metrics.py
import pytest
from src.sim.event_metrics import EventMetrics
from src.sim.event import EventType
from src.controller.command import MoveCommand

def test_metrics_counts_command_events(system):
    # 1. 테스트용 독립 metrics 생성 및 구독
    test_metrics = EventMetrics()
    system.bus.subscribe(EventType.COMMAND_STARTED, test_metrics.handle)
    system.bus.subscribe(EventType.COMMAND_SUCCESS, test_metrics.handle)

    # 2. 명령 실행
    manager_a = system.managers.get("A")
    manager_a.add_command(MoveCommand(alt=10, az=10))

    # 3. 충분히 업데이트 (성공할 때까지)
    for _ in range(10):
        system.update(1.0)

    # 4. 검증: 숫자가 정확히 올라갔는가?
    assert test_metrics.command_started == 1
    assert test_metrics.command_success == 1
    assert test_metrics.command_failed == 0