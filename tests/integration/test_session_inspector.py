# tests/integration/test_session_inspector.py

import json
import pytest
from src.sim.session_inspector import SessionInspector

def test_error_cause_extraction(tmp_path):
    # 1. 실패한 세션 데이터 위조 (Mock Data)
    session_id = "session_fail_test"
    session_dir = tmp_path / session_id
    session_dir.mkdir()
    
    events = [
        {"type": "COMMAND_STARTED", "sim_time": 10.0, "payload": {"cmd": "MOVE"}},
        {"type": "COMMAND_FAILED", "sim_time": 15.5, "payload": {"reason": "Collision Detected"}}
    ]
    
    log_path = session_dir / "events.jsonl"
    with open(log_path, "w") as f:
        for e in events:
            f.write(json.dumps(e) + "\n")

    # 2. Inspector 가동
    inspector = SessionInspector(storage_path=tmp_path)
    summary = inspector.get_error_summary(session_id)

    # 3. 검증
    assert summary["error_type"] == "COMMAND_FAILED"
    assert summary["reason"] == "Collision Detected"
    assert summary["last_sim_time"] == 15.5