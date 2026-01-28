"""
Main entry point for the Radio Telescope Control System.

This file initializes the telescope hardware abstraction,
the CommandManager, and runs the main control loop.

Responsibilities:
- System initialization
- Continuous update loop
- High-level execution flow

Note:
- Telescope handles physical movement only
- CommandManager controls command sequencing and lifecycle
"""
#메인으로 실행할 프로그램

import time
from src.controller.telescope import Telescope
from src.controller.command_manager import CommandManager
from src.controller.command import MoveCommand, StopCommand

def main():
    dt = 0.1

    telescope = Telescope()
    manager = CommandManager()

    # 시나리오 등록
    manager.add_command(MoveCommand(10, 10))
    manager.add_command(MoveCommand(20, 20))
    manager.add_command(StopCommand())

    print("[SYSTEM] Telescope control system started.")
    
    # Main control loop (system stays alive and waits for commands)
    while True:
        telescope.update(dt)
        manager.update(telescope, dt)
        time.sleep(dt)

if __name__ == "__main__":
    main()
