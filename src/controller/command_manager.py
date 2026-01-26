#여러 command의 실행 순서와 상태를 관리하는 중앙 제어자

from src.controller.command import (
    CMD_SUCCESS,
    CMD_FAILED,
    CMD_ABORTED,
)

class CommandManager:
    def __init__(self):
        self.queue = []
        self.current = None

    def add_command(self, cmd):
        self.queue.append(cmd)

    def update(self, telescope, dt):
        # 실행 중인 Command가 없으면 다음 Command 실행
        if self.current is None and self.queue:
            self.current = self.queue.pop(0)
            self.current.execute(telescope)

        if self.current:
            self.current.update(telescope, dt)

            # Command 종료 처리
            if self.current.state in (CMD_SUCCESS, CMD_FAILED, CMD_ABORTED):
                self.current = None
