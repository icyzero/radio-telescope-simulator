# tests/unit/test_event_history.py
from src.sim.event import Event, EventType
import pytest

def test_event_history_records_with_metadata(system):
    # 1. 이벤트 수동 발행
    test_payload = {"reason": "test"}
    system.bus.publish(Event(EventType.SYSTEM_PAUSED, "SYSTEM", test_payload))

    # 2. 기록 조회
    history = system.bus.get_history(EventType.SYSTEM_PAUSED)

    # 3. 검증
    assert len(history) == 1
    event = history[0]
    assert event.payload["reason"] == "test"
    assert hasattr(event, 'wall_time')  # timestamp 존재 확인