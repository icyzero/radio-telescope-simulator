from src.controller.command import MoveCommand, StopCommand
from src.controller.command_manager import CommandManager
from src.controller.telescope import Telescope
import time

dt = 0.1

telescope = Telescope()
mgr = CommandManager()

mgr.add_command(MoveCommand(10, 10))
mgr.add_command(MoveCommand(20, 20))
mgr.add_command(StopCommand())
mgr.add_command(MoveCommand(30, 30))

while True:
    mgr.update(telescope, dt)
    telescope.update(dt)
    time.sleep(dt)
