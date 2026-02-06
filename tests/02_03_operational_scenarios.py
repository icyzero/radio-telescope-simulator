from src.controller.telescope import Telescope
from src.controller.command_manager import CommandManager
from src.controller.command import MoveCommand, StopCommand

def scenario_emergency_stop():
    print("\n--- Scenario A: Emergency STOP during MOVE ---")

    telescope = Telescope()
    mgr = CommandManager(telescope)

    mgr.add_command(MoveCommand(80, 80, timeout=0.3)) #timeout 실패 유도

    for _ in range(5):
        mgr.update(telescope, dt=0.1)

    mgr.add_command(StopCommand())

    mgr.add_command(MoveCommand(80, 80, timeout=10.0)) #정상 움직임

    dt = 0.1
    for step in range(200):
        if step == 30:
            mgr.add_command(StopCommand())

        mgr.update(telescope, dt)
        telescope.update(dt)

if __name__ == "__main__":
    scenario_emergency_stop()
