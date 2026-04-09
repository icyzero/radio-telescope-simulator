# tests/integration/test_safety_guard.py

import pytest
from src.scheduler.scheduler import SystemController
from src.sim.remote_gate import RemoteCommandGate
import json

def test_out_of_range_rejection():
    ctrl = SystemController()
    gate = RemoteCommandGate(ctrl)

    # 1. 잘못된 고도 입력 (음수) - JSON 문자열로 변환하여 전달
    bad_data = json.dumps({
        "type": "MOVE", 
        "manager": "Main", # 매니저 이름도 챙겨주세요!
        "params": {"alt": -10.0, "az": 180.0}
    })
    
    # 🚨 메서드 이름을 통합된 버전으로 변경
    response = gate.process_json_command(bad_data)

    assert response["status"] == "REJECTED"
    assert "Altitude out of range" in response["reason"]
    # 2. 시스템 STOPPED 상태일 때 명령 주입
    ctrl.global_stop()
    
    # JSON 문자열로 변환 및 매니저 추가
    move_data = json.dumps({
        "type": "MOVE", 
        "manager": "Main", 
        "params": {"alt": 45.0, "az": 180.0}
    })
    
    # 🚨 여기도 이름을 process_json_command로 변경!
    response = gate.process_json_command(move_data)

    assert response["status"] == "REJECTED"
    assert "STOPPED mode" in response["reason"]