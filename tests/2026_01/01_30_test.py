from src.controller.command import MoveCommand, StopCommand, Command, CMD_ABORTED
from src.controller.command_manager import CommandManager
from src.controller.telescope import Telescope
import time

dt = 0.1

telescope = Telescope()
mgr = CommandManager()

mgr.add_command(MoveCommand(10, 10, scheduled_at=5.0))
mgr.add_command(MoveCommand(15, 15, scheduled_at=10.0))
mgr.add_command(StopCommand())

while True:
    telescope.update(dt)
    mgr.update(telescope, dt)

    if mgr.current is None and not mgr.queue: #command가 끝나면 while문 탈출
        print("[SYSTEM] All commands finished.")
        break

    time.sleep(dt)
