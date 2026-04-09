import json
from src.controller.command import MoveCommand
from src.controller.safety import SafetyGuard # 추가
from src.sim.event import EventType

class RemoteCommandGate:
    def __init__(self, controller):
        self.controller = controller

    def process_json_command(self, raw_json: str):
        try:
            data = json.loads(raw_json)
            # action 또는 type 중 설계자님이 정의하신 키 사용 (여기선 action으로 통일)
            action = data.get("action") or data.get("type") 
            params = data.get("params", {})
            mgr_name = data.get("manager")

            # [1단계] SafetyGuard를 통한 사전 검증
            if action == "MOVE":
                is_safe, msg = SafetyGuard.validate_move(params, self.controller.mode)
                if not is_safe:
                    # 이벤트 버스에 실패 기록
                    self.controller.emit(EventType.COMMAND_FAILED, "SafetyGuard", {"reason": msg})
                    return {"status": "REJECTED", "reason": msg}

            # [2단계] 전역 액션 처리 (GET_STATUS 등)
            if action == "GET_STATUS":
                return {"status": "SUCCESS", "data": self.controller.get_telemetry()}

            # [3단계] 매니저 확인 및 명령 실행
            if not mgr_name or mgr_name not in self.controller.managers:
                return {"status": "ERROR", "msg": f"Manager '{mgr_name}' not found"}

            cmd_mgr = self.controller.managers[mgr_name]

            if action == "MOVE":
                alt, az = params.get("alt"), params.get("az")
                new_cmd = MoveCommand(alt, az)
                
                # 시스템 모드에 따른 명령 주입 (NORMAL/PAUSED 등)
                cmd_mgr.add_command(new_cmd, system_mode=self.controller.mode)
                
                return {"status": "SUCCESS", "msg": f"MoveCommand({alt}, {az}) queued"}

            return {"status": "ERROR", "msg": f"Unsupported action: {action}"}

        except Exception as e:
            return {"status": "EXCEPTION", "msg": str(e)}