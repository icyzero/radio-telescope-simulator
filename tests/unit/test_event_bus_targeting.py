# tests/unit/test_event_bus_targeting.py
from src.sim.event import EventType
from src.controller.command import MoveCommand

def test_subscriber_receives_only_targeted_events(system):
    received_starts = []
    received_stops = []

    # 1. 각각 다른 이벤트에 구독
    system.bus.subscribe(EventType.COMMAND_STARTED, lambda e: received_starts.append(e))
    system.bus.subscribe(EventType.MANAGER_CRITICAL_STOP, lambda e: received_stops.append(e))

    # 2. 명령 시작 이벤트만 유발
    manager = system.managers["A"]
    manager.add_command(MoveCommand(0, 0))
    system.update(0.1)

    # 3. 검증: START는 받았지만 STOP은 받지 않아야 함
    assert len(received_starts) == 1
    assert len(received_stops) == 0

def test_multiple_subscribers_receive_same_event(system):
    """하나의 이벤트가 발행되었을 때, 해당 타입을 구독한 모든 핸들러가 호출되어야 함"""
    results = []

    # 1. 동일한 이벤트 타입(COMMAND_STARTED)에 두 개의 서로 다른 핸들러 등록
    def handler_one(event):
        results.append("HANDLER_ONE_CALLED")

    def handler_two(event):
        results.append("HANDLER_TWO_CALLED")

    system.bus.subscribe(EventType.COMMAND_STARTED, handler_one)
    system.bus.subscribe(EventType.COMMAND_STARTED, handler_two)

    # 2. 이벤트 유발 (명령 투입)
    manager = system.managers["A"]
    manager.add_command(MoveCommand(alt=10, az=10))
    system.update(0.1)

    # 3. 검증: 두 핸들러 모두 호출되었는지 확인
    assert "HANDLER_ONE_CALLED" in results
    assert "HANDLER_TWO_CALLED" in results
    assert len(results) == 2