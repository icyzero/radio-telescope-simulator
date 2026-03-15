# src/sim/event_persistence.py
import json

class EventPersistence:
    @staticmethod
    def save(events, filepath):
        """이벤트 리스트를 JSON 파일로 직렬화하여 저장"""
        data = []

        for e in events:
            # Event 객체를 JSON 직화 가능한 딕셔너리로 변환
            data.append({
                "type": e.type.name,        # Enum은 이름으로 저장
                "source": e.source,
                "payload": e.payload,
                "sim_time": e.sim_time,
                "wall_time": e.timestamp.isoformat() # datetime은 ISO 문자열로
            })

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)