# tests/integration/test_telemetry.py

import time
import json
import pytest
from src.scheduler.scheduler import SystemController
from src.sim.remote_gate import RemoteCommandGate
from src.controller.command_manager import CommandManager
from src.controller.telescope import Telescope
from src.controller.enums import TelescopeState

def test_telemetry_data_integrity():
    ctrl = SystemController()
    tel = Telescope()
    tel.slew_rate = 20.0
    tel.MAX_SPEED = 100.0
    tel.MIN_SPEED = 5.0 # 최소 속도를 확 높여보세요
    tel.alt, tel.az = 0.0, 0.0

    cmd_mgr = CommandManager("Main", tel)
    ctrl.register_manager("Main", cmd_mgr)
    gate = RemoteCommandGate(ctrl)

    # 명령 주입
    gate.process_json_command(json.dumps({
        "manager": "Main", "action": "MOVE", "params": {"alt": 0.0, "az": 100.0}
    }))

    # 업데이트
    ctrl.update(0.5)

    # 확인
    print(f"\n[FINAL DEBUG] az: {tel.az}, v_az: {tel.v_az}, dist: {tel.az_error}")
    
    assert tel.az > 0.0, f"속도({tel.v_az})가 여전히 0입니다!"