from src.controller.command import MoveCommand, StopCommand, Command, CMD_ABORTED
from src.controller.command_manager import CommandManager
from src.controller.telescope import Telescope
import time

class FailingCommand(Command):
    def execute(self, telescope):
        print("[CMD] FailingCommand EXECUTE")
        self.state = CMD_ABORTED

dt = 0.1

telescope = Telescope()
mgr = CommandManager()

mgr.add_command(MoveCommand(10, 10))
mgr.add_command(FailingCommand())
mgr.add_command(MoveCommand(20, 20))
mgr.add_command(StopCommand())

while True:
    telescope.update(dt)
    mgr.update(telescope, dt)

    if mgr.current is None and not mgr.queue: #command가 끝나면 while문 탈출
        print("[SYSTEM] All commands finished.")
        break

    time.sleep(dt)
