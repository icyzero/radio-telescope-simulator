# tests/integration/test_final_chaos.py

import json
import random
from src.scheduler.scheduler import SystemController
from src.sim.remote_gate import RemoteCommandGate

def test_system_under_chaos():
    ctrl = SystemController()
    gate = RemoteCommandGate(ctrl)
    
    # 1. 명령 홍수 (Command Flood) + 한계점 공격
    for i in range(100):
        # 80%는 정상, 20%는 비정상 좌표 생성
        is_valid = random.random() > 0.2
        alt = random.uniform(0, 90) if is_valid else random.uniform(-10, -1)
        az = random.uniform(0, 360)

        cmd = json.dumps({
            "action": "MOVE",
            "manager": "Main",
            "params": {"alt": alt, "az": az}
        })
        gate.process_json_command(cmd)

    # 2. 교차 간섭 (Interference): 이동 중 설정 변경 및 진단
    # 속도를 극한으로 높였다 낮췄다 반복
    for speed in [5.0, 45.0, 10.0]:
        gate.process_json_command(json.dumps({
            "action": "CONFIG_UPDATE",
            "params": {"slew_rate": speed}
        }))
        # 그 와중에 진단 보고서 요청
        diag_res = gate.process_json_command(json.dumps({"action": "DIAGNOSTICS"}))
        assert diag_res["status"] == "SUCCESS"

    # 3. 최종 무결성 검증
    report = ctrl.get_diagnostics()
    perf = report["performance"]
    
    print(f"Total: {perf['total_commands']}, Failed: {perf['failed_count']}")
    
    # 총 명령 수는 103개(Flood 100 + Config 3)여야 함
    assert int(perf["total_commands"]) >= 103
    # 실패 카운트가 0보다 커야 함 (랜덤 공격 성공 확인)
    assert int(perf["failed_count"]) > 0