from src.controller.command import (
    CMD_SUCCESS,
    CMD_FAILED,
    CMD_ABORTED,
)

class CommandManager:
    def __init__(self):
        self.queue = []
        self.current_cmd = None

    def add_command(self, cmd):
        self.queue.append(cmd)

    def update(self, telescope, dt):
        # 실행 중인 Command가 없으면 다음 Command 실행
        if self.current_cmd is None:
            if not self.queue:
                return
            self.current_cmd = self.queue.pop(0)
            self.current_cmd.execute(telescope)

        # 현재 Command 업데이트
        self.current_cmd.update(telescope, dt)

        # Command 종료 처리
        if self.current_cmd.state in (CMD_SUCCESS, CMD_FAILED, CMD_ABORTED):
            self.current_cmd = None
