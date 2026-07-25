# src/sim/event_replay.

def sort_by_sim_time(events):
    """이벤트 리스트를 sim_time 기준으로 정렬 (event_timeline.py, event_replayer.py와 공용)"""
    return sorted(events, key=lambda e: e.sim_time)

class EventOrderedReader:
    def __init__(self, events):
        """저장된 이벤트를 시간 순서대로 정렬하여 준비"""
        self.events = sort_by_sim_time(events)

    def replay(self):
        """이벤트를 하나씩 순차적으로 내뱉는 재생기"""
        for event in self.events:
            yield event