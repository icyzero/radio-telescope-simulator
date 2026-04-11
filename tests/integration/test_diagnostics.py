# tests/integration/test_diagnostics.py

import pytest
from src.scheduler.scheduler import SystemController
from src.sim.remote_gate import RemoteCommandGate
import json

def test_diagnostics_report_integrity():
    ctrl = SystemController()
    # Metrics 모듈이 있다고 가정 (없다면 위 get_diagnostics에서 기본값 처리됨)
    gate = RemoteCommandGate(ctrl)
    
    # 1. 초기 진단 리포트 확인
    response = gate.process_json_command(json.dumps({"action": "DIAGNOSTICS"}))
    assert response["status"] == "SUCCESS"
    assert response["diagnostics"]["performance"]["total_commands"] == 0

    # 2. 의도적 실패 유도 (잘못된 좌표 전송)
    bad_move = json.dumps({
        "action": "MOVE", 
        "manager": "Main", 
        "params": {"alt": -5.0, "az": 100}
    })
    gate.process_json_command(bad_move)

    # 3. 진단 리포트 갱신 확인
    new_response = gate.process_json_command(json.dumps({"action": "DIAGNOSTICS"}))
    perf = new_response["diagnostics"]["performance"]
    
    # 실패한 명령이 카운트에 반영되었는지 확인
    # (Metrics 구현 방식에 따라 숫자는 달라질 수 있음)
    assert perf["failed_count"] > 0