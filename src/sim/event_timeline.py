# src/sim/event_timeline.py

class EventTimeline:
    def __init__(self, events):
        # sim_time 기준으로 정렬하여 시간 순서를 보장합니다.
        self.events = sorted(events, key=lambda e: e.sim_time)

    def get_types(self):
        """이벤트 타입의 흐름을 리스트로 반환"""
        return [e.type for e in self.events]

    def duration_between(self, start_type, end_type):
        """두 이벤트 타입 사이의 소요 시간(sim_time 차이)을 계산"""
        start_time = None
        end_time = None

        for e in self.events:
            # 첫 번째로 발견되는 시작 이벤트를 기록
            if e.type == start_type and start_time is None:
                start_time = e.sim_time

            # 시작 이벤트 이후에 나타나는 종료 이벤트를 기록
            if e.type == end_type and start_time is not None:
                end_time = e.sim_time
                break # 구간이 정해졌으므로 중단

        if start_time is None or end_time is None:
            return None

        return end_time - start_time