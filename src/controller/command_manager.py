#여러 command의 실행 순서와 상태를 관리하는 중앙 제어자

from src.controller.command import (
    CMD_SUCCESS,
    CMD_FAILED,
    CMD_ABORTED,
)
from src.utils.logger import log

class CommandManager:
    def __init__(self):
        self.queue = []
        self.current = None
        self.time = 0.0

    def add_command(self, cmd):
        self.queue.append(cmd)

    def update(self, telescope, dt):
        self.time += dt
        # 1. 실행 중인 Command가 없으면 다음 Command 실행
        if self.current is None and self.queue:
            next_cmd = self.queue[0]
            
            if self.time >= next_cmd.scheduled_at:
                self.current = self.queue.pop(0)
                self.current.execute(telescope)

        if self.current:
            self.current.update(telescope, dt)

            # 2. Command 종료 처리
            if self.current.state in (CMD_SUCCESS, CMD_FAILED, CMD_ABORTED):
                # 3. Telescope가 STOPPED면 시스템 레벨 중단
                if telescope.is_stopped():
                    log("[SYSTEM] Telescope STOPPED. Command queue halted.")
                    self.current = None
                    self.queue.clear()   # ← 핵심: 더 이상 진행하지 않음
                    return

                # 4. 정상적인 Command 종료 → 다음 Command로
                self.current = None