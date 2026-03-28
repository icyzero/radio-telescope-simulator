# tests/integration/test_migration.py
import pytest
from src.sim.event_validator import EventValidator
from src.sim.event import Event, EventType

def test_backward_compatibility_v1_to_current():
    """v1 스타일의 구형 로그가 현재 시스템에서 정상 통과하는지 확인"""
    # v1 데이터 (버전 필드가 없거나 1인 경우)
    legacy_event = Event(
        type=EventType.COMMAND_SUCCESS,
        source="Mgr",
        payload={"cmd_type": "MOVE", "result_state": {"manager_state": "IDLE"}},
        version=1 # 혹은 생략
    )
    
    # 현재 시스템의 Validator가 v1 규칙을 적용해 통과시켜야 함
    assert EventValidator.validate(legacy_event) is True

def test_v2_strict_validation():
    """v2 데이터는 더 엄격한 규칙(예: precision 필드)을 지켜야 함"""
    v2_event_invalid = Event(
        type=EventType.COMMAND_SUCCESS,
        source="Mgr",
        payload={"cmd_type": "MOVE", "result_state": {}},
        version=2
    )

    with pytest.raises(ValueError) as excinfo:
        EventValidator.validate(v2_event_invalid)
    
    # 🔥 수정: 'required'를 포함하거나, 더 유연하게 핵심 단어만 체크
    assert "Missing required field 'precision'" in str(excinfo.value)