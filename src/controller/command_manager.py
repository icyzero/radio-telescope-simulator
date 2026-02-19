#여러 command의 실행 순서와 상태를 관리하는 중앙 제어자

from src.controller.state_rules import STATE_COMMAND_RULES, CommandDecision

from src.controller.command import (
    CMD_SUCCESS,
    CMD_FAILED,
    CMD_ABORTED,
)
from src.utils.logger import log

class CommandManager:
    def __init__(self, name, telescope):
        self.name = name
        self.telescope = telescope
        self.queue = []
        self.current = None
        self.time = 0.0

    def add_command(self, cmd): #movig중에 새로운 목표 추가시 큐에만 추가
        state = self.telescope.state
        decision = STATE_COMMAND_RULES[state].get(cmd.type, CommandDecision.REJECT)
        log(f"[DEBUG] add_command: state={state.name}, cmd={cmd.type.name}", prefix=self.name)


        if decision == CommandDecision.EXECUTE:        
            log(f"[CMD] {cmd.type.name} accepted ({decision.name})", prefix=self.name)
            
            if self.current:
                self.current.abort(prefix=self.name) #기존 Command 중단
                self.current = None
            
            self.queue.clear() #queue 무효화
            self.current = cmd
            cmd.execute(self.telescope, prefix=self.name)
            
        elif decision == CommandDecision.PENDING:
            self.queue.append(cmd)
            self.queue.sort(key=lambda c: c.priority)
            log(f"[CMD] {cmd.type.name} accepted ({decision.name})", prefix=self.name)

        else: #REJECT
            log(f"[CMD] {cmd.type.name} rejected (state={state.name})", prefix=self.name)

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
            self.current.abort(prefix=self.name)
            self.current = None
        self.queue.clear()
        self.telescope.stop()
        log("[MANAGER] Emergency STOP executed. All cleared.", prefix=self.name)

    def update(self, dt):
        self.time += dt
        
        # 1. 실행 중인 Command가 없으면 다음 Command 실행
        if self.current is None and self.queue:
            next_cmd = self.queue[0]
            
            if self.time >= next_cmd.scheduled_at:
                self.current = self.queue.pop(0)
                self.current.execute(self.telescope, prefix=self.name)

        if self.current:
            self.current.update(self.telescope, dt, prefix=self.name)

            # 2. Command 종료 처리
            if self.current.state in (CMD_SUCCESS, CMD_FAILED, CMD_ABORTED):
                # 3. Telescope가 STOPPED면 시스템 레벨 중단
                if self.telescope.is_stopped():
                    log("[MANAGER] Telescope STOPPED. Command queue halted.", prefix=self.name)
                    self.current = None
                    self.queue.clear()   # ← 핵심: 더 이상 진행하지 않음
                    return

                # 4. 정상적인 Command 종료 → 다음 Command로
                self.current = None