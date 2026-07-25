# src/sim/bus.py
from src.utils.logger import log
from src.sim.event_validator import EventValidator

class EventBus:
    def __init__(self, archive_manager=None):
        self._history = []
        self._subscribers = {}
        self._global_subscribers = []
        self.archive_manager = archive_manager

    def subscribe(self, event_type, handler=None):
        """특정 이벤트 타입만 구독하려면 subscribe(event_type, handler),
        모든 이벤트를 구독하려면 subscribe(handler)로 호출"""
        if handler is None:
            handler = event_type
            if handler not in self._global_subscribers:
                self._global_subscribers.append(handler)
            return
        """특정 이벤트 타입에 대해서만 구독 신청"""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []

        if handler not in self._subscribers[event_type]:
            self._subscribers[event_type].append(handler)

    def publish(self, event):
        """이벤트를 검증하고, 기록하고, 구독 중인 객체들에게 전파하고, 필요하면 아카이빙까지 함"""
        # 0. 검증 - 스키마 위반 이벤트는 여기서 즉시 예외
        EventValidator.validate(event)

        # 1. 기록
        self._history.append(event)

        # 2. 아카이빙 (archive_manager가 주입된 경우에만)
        if self.archive_manager:
            self.archive_manager.log_event(self._event_to_dict(event))

        # 해당 이벤트 타입을 기다리는 핸들러들만 추출
        handlers = self._subscribers.get(event.type, [])
        
        # 3. 전파 (Dispatcher 기능)
        for handler in self._global_subscribers + handlers:
            try:
                handler(event)
            except Exception as e:
                # [원칙 1, 2 준수] 구독자의 실수가 시스템 전체를 무너뜨리지 않도록 방어
                log(f"[ERROR] EventBus: Subscriber failed with error: {e}")

    @staticmethod
    def _event_to_dict(event) -> dict:
        """Event를 JSON 직렬화 가능한 dict로 변환 (ArchiveManager.log_event용)"""
        return {
            "id": event.id,
            "type": event.type.name,
            "source": event.source,
            "payload": event.payload,
            "sim_time": event.sim_time,
            "timestamp": event.timestamp.isoformat(),
            "version": event.version,
        }

    def get_events(self, type=None, source=None, start_time=None, end_time=None):
        """조건에 맞는 이벤트만 필터링하여 반환"""
        events = self._history # 내부 히스토리 리스트 (원본 보존을 위해 참조)

        if type is not None:
            events = [e for e in events if e.type == type]

        if source is not None:
            events = [e for e in events if e.source == source]

        if start_time is not None:
            events = [e for e in events if e.sim_time >= start_time]

        if end_time is not None:
            events = [e for e in events if e.sim_time <= end_time]

        return events
    
    def get_history(self, event_type=None):
        """특정 타입 혹은 전체 이벤트 기록을 안전하게 복사해서 반환"""
        if event_type is None:
            return list(self._history)
        return [e for e in self._history if e.type == event_type]
    
    def clear(self):
        """테스트 간 간섭 방지를 위한 초기화"""
        self._history.clear()
    
    def unsubscribe(self, callback):
        """구독 해지 기능 (옵션)"""
        if callback in self._subscribers:
            self._subscribers.remove(callback)