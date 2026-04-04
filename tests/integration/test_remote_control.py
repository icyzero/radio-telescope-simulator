# tests/integration/test_remote_control.py

from src.scheduler.scheduler import SystemController
from src.sim.remote_gate import RemoteCommandGate
from src.controller.command_manager import CommandManager
from src.controller.telescope import Telescope
import json

def test_remote_json_injection():
    # 1. 환경 구축
    ctrl = SystemController()
    tel = Telescope()
    
    # 2. 설계자님의 원칙: Telescope를 품은 CommandManager 생성 및 등록
    # CommandManager.__init__(self, name, telescope)
    cmd_mgr = CommandManager("MainTelescope", tel)
    ctrl.register_manager("MainTelescope", cmd_mgr) # 여기서 set_event_emitter 자동 호출됨!
    
    gate = RemoteCommandGate(ctrl)

    # 3. 외부 JSON 명령 모사
    mock_json = json.dumps({
        "manager": "MainTelescope",
        "action": "MOVE",
        "params": {"alt": 45.0, "az": 180.0}
    })

    # 4. 게이트웨이 통과
    response = gate.process_json_command(mock_json)

    # 5. 검증
    assert response["status"] == "SUCCESS"
    # CommandManager의 큐에 명령이 대기 중인지 확인
    assert len(cmd_mgr.queue) == 1 or cmd_mgr.current is not None