# src/sim/event_persistence.py
import json
from datetime import datetime
from src.sim.event import Event, EventType

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
        
        pass

    @staticmethod
    def load(filepath):
        """JSON 파일을 읽어 Event 객체 리스트로 복원"""
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        events = []
        for e in data:
            # 텍스트로 저장된 이름을 다시 Enum 멤버로 복구
            # 예: "COMMAND_STARTED" -> EventType.COMMAND_STARTED
            event_obj = Event(
                type=EventType[e["type"]], 
                source=e["source"],
                payload=e["payload"],
                sim_time=e["sim_time"],
                timestamp=datetime.fromisoformat(e["wall_time"])
            )
            events.append(event_obj)

        return events