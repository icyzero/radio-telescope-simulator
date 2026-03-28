# src/sim/event_schema.py

from src.sim.event import EventType

class EventSchema:
    # 버전별 필수 필드 정의 (백과사전 역할)
    SCHEMAS = {
        1: {
            EventType.COMMAND_SUCCESS: ["cmd_type", "result_state"],
            EventType.COMMAND_FAILED: ["cmd_type", "reason", "result_state"],
        },
        2: {
            # 예: v2에서는 'precision'이나 'timestamp'가 필수라고 가정
            EventType.COMMAND_SUCCESS: ["cmd_type", "result_state", "precision"],
        }
    }

    @staticmethod
    def get_required_fields(event_type, version):
        # 지원하지 않는 버전이면 v1을 기본값으로 하거나 빈 리스트 반환
        version_schema = EventSchema.SCHEMAS.get(version, EventSchema.SCHEMAS[1])
        return version_schema.get(event_type, [])