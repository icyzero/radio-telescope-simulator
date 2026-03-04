# src/sim/bus.py
from src.utils.logger import log

class EventBus:
    def __init__(self):
        self._history = []
        self._subscribers = []

    def subscribe(self, callback):
        """이벤트를 구독할 콜백 등록"""
        if callback not in self._subscribers:
            self._subscribers.append(callback)

    def publish(self, event):
        """이벤트를 발행하고 모든 구독자에게 알림"""
        # 1. 기록 (기존 기능 유지)
        self._history.append(event)
        
        # 2. 전파 (Dispatcher 기능)
        for subscriber in self._subscribers:
            try:
                subscriber(event)
            except Exception as e:
                # [원칙 1, 2 준수] 구독자의 실수가 시스템 전체를 무너뜨리지 않도록 방어
                log(f"[ERROR] EventBus: Subscriber failed with error: {e}")

    def get_events(self, event_type=None):
        """기존 테스트 코드와의 하위 호환성 유지"""
        if event_type:
            return [e for e in self._history if e.type == event_type]
        return self._history
    
    def unsubscribe(self, callback):
        """구독 해지 기능 (옵션)"""
        if callback in self._subscribers:
            self._subscribers.remove(callback)