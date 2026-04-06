# src/sim/remote_gate.py

import json
from src.controller.command import MoveCommand # 실제 프로젝트 경로에 맞춰 임포트

class RemoteCommandGate:
    def __init__(self, controller):
        self.controller = controller

    def process_json_command(self, raw_json: str):
        try:
            data = json.loads(raw_json)
            action = data.get("action")
            params = data.get("params", {})

            # [1단계] 전역 액션 처리 (매니저 이름이 필요 없는 경우)
            if action == "GET_STATUS":
                return {
                    "status": "SUCCESS", 
                    "data": self.controller.get_telemetry()
                }

            # [2단계] 특정 매니저가 필요한 액션 처리
            mgr_name = data.get("manager")
            if not mgr_name or mgr_name not in self.controller.managers:
                return {"status": "ERROR", "msg": f"Manager '{mgr_name}' not found or required"}

            cmd_mgr = self.controller.managers[mgr_name]

            # 2. 액션 해석 및 실행
            if action == "MOVE":
                alt = params.get("alt")
                az = params.get("az")
                
                # Command 객체 생성
                new_cmd = MoveCommand(alt, az)
                
                # CommandManager의 add_command 호출 (설계자님의 원칙 준수)
                # 현재 시스템 모드를 전달 (기본값 NORMAL)
                mode = getattr(self.controller, 'mode', 'NORMAL')
                cmd_mgr.add_command(new_cmd, system_mode=mode)
                
                return {"status": "SUCCESS", "msg": f"MoveCommand({alt}, {az}) queued via {mgr_name}"}

            return {"status": "ERROR", "msg": f"Unsupported action: {action}"}

        except Exception as e:
            return {"status": "EXCEPTION", "msg": str(e)}