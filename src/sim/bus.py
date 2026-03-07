# src/sim/bus.py
from src.utils.logger import log

class EventBus:
    def __init__(self):
        self._history = []
        self._subscribers = {}

    def subscribe(self, event_type, handler):
        """특정 이벤트 타입에 대해서만 구독 신청"""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []

        if handler not in self._subscribers[event_type]:
            self._subscribers[event_type].append(handler)

    def publish(self, event):
        """이벤트를 기록하고, 해당 타입을 구독 중인 객체들에게만 전파"""
        # 1. 기록
        self._history.append(event)

        # 해당 이벤트 타입을 기다리는 핸들러들만 추출
        handlers = self._subscribers.get(event.type, [])
        
        # 2. 전파 (Dispatcher 기능)
        for handler in handlers:
            try:
                handler(event)
            except Exception as e:
                # [원칙 1, 2 준수] 구독자의 실수가 시스템 전체를 무너뜨리지 않도록 방어
                log(f"[ERROR] EventBus: Subscriber failed with error: {e}")

    def get_events(self, event_type=None):
        """기존 테스트 코드와의 하위 호환성 유지"""
        if event_type:
            return [e for e in self._history if e.type == event_type]
        return self._history
    
    def get_history(self, event_type=None):
        """특정 타입 혹은 전체 이벤트 기록을 안전하게 복사해서 반환"""
        if event_type is None:
            return list(self._history)
        return [e for e in self._history if e.type == event_type]
    
    def unsubscribe(self, callback):
        """구독 해지 기능 (옵션)"""
        if callback in self._subscribers:
            self._subscribers.remove(callback)