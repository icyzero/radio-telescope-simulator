# tests/integration/test_config_tuning.py

import pytest
import json
from src.scheduler.scheduler import SystemController
from src.controller.telescope import Telescope
from src.controller.command_manager import CommandManager
from src.sim.remote_gate import RemoteCommandGate

def test_runtime_slew_rate_tuning():
    ctrl = SystemController()
    tel = Telescope(slew_rate=10.0) # 기본 속도 10
    mgr = CommandManager("Main", tel)
    ctrl.register_manager("Main", mgr)
    gate = RemoteCommandGate(ctrl)

    # 1. 속도 변경 명령 실행
    config_data = json.dumps({
        "action": "CONFIG_UPDATE",
        "params": {"slew_rate": 25.0}
    })
    response = gate.process_json_command(config_data)

    # 2. 검증: 응답 결과 및 실제 객체 값 확인
    assert response["status"] == "SUCCESS"
    assert tel.slew_rate == 25.0
    
    # 3. 비정상 값 차단 확인 (SafetyGuard 연동)
    bad_config = json.dumps({
        "action": "CONFIG_UPDATE",
        "params": {"slew_rate": -5.0}
    })
    bad_response = gate.process_json_command(bad_config)
    assert bad_response["status"] == "REJECTED"