# src/sim/event_replay.py

class EventReplay:
    def __init__(self, events):
        """저장된 이벤트를 시간 순서대로 정렬하여 준비"""
        self.events = sorted(events, key=lambda e: e.sim_time)

    def replay(self):
        """이벤트를 하나씩 순차적으로 내뱉는 재생기"""
        for event in self.events:
            yield event