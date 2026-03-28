# src/controller/command_manager.py
#여러 command의 실행 순서와 상태를 관리하는 중앙 제어자

from src.controller.state import IdleState, LockedState
from src.utils.logger import log


class CommandManager:
    def __init__(self, name, telescope):
        self.name = name
        self.telescope = telescope
        self.state = IdleState()
        self.queue = []
        self.current = None
        self.time = 0.0
        self.emit = lambda type, source, payload=None: None

    def set_event_emitter(self, emit_func):
        """SystemController로부터 이벤트 발행 함수를 주입받음"""
        self.emit = emit_func

    def add_command(self, cmd, system_mode="NORMAL"): #movig중에 새로운 목표 추가시 큐에만 추가
        return self.state.handle_add_command(self, cmd, system_mode)

    def cancel_pending(self):
        """
        cancel all peding (not yet started) commands.
        Running command is never interrupted.   
        """
        self.queue.clear()
        log("[MANAGER] Pending commmands cancelled.", prefix=self.name)

    def stop(self): # 긴급 정지를 위한 메서드
        #시스템 전체를 즉시 중단하고 큐를 비움
        if self.current:
            self.current.abort(prefix=self.name) # 현재 진행 중인 MOVE를 ABORTED로!
            self.current = None
        self.queue.clear()
        self.telescope.stop()
        log("[MANAGER] Emergency STOP executed. All cleared.", prefix=self.name)

    def update(self, dt):
        return self.state.handle_update(self, dt)
    
    def get_state(self) -> dict:
        """현재 매니저와 조종 중인 망원경의 모든 상태를 반환"""
        return {
            "manager_state": self.state,
            # 망원경이 연결되어 있다면 망원경의 get_state()를 호출
            "telescope": self.telescope.get_state() if hasattr(self, 'telescope') else None
        }
        
    def set_state(self, state: dict):
        self.state = state.get("manager_state", "IDLE")
        if "telescope" in state and hasattr(self, 'telescope'):
            self.telescope.set_state(state["telescope"])

    @property #하위호환성 유지
    def _is_critical(self):
        """상태 객체가 LockedState인지 여부를 반환하여 하위 호환성 유지"""
        return isinstance(self.state, LockedState)

    def reset_critical(self):
        return self.state.handle_reset(self)