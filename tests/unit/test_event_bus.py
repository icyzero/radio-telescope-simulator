# tests/unit/test_event_bus.py
import pytest

def test_event_bus_reliability(system):
    """구독자가 에러를 내도 시스템은 계속 동작해야 함"""
    results = []

    def broken_listener(event):
        raise RuntimeError("I am a broken subscriber")

    def healthy_listener(event):
        results.append("SUCCESS")

    system.bus.subscribe(broken_listener)
    system.bus.subscribe(healthy_listener)

    # 이벤트 발행
    system.global_pause()

    # 검증: 에러가 발생했음에도 두 번째 구독자까지 실행되었는가?
    assert "SUCCESS" in results