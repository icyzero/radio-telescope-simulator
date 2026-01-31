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
"""
Main control loop for the radio telescope simulator.

This loop is intentionally designed as an infinite loop (`while True`)
to emulate real-world telescope control systems, which operate in an
always-on, event-driven manner rather than executing a finite task.

Design principles:

- Time-driven simulation:
  The system advances in fixed time steps (`dt`), allowing deterministic
  and testable physical motion.

- Separation of responsibilities:
  - Telescope updates only its physical state.
  - CommandManager manages command execution order and lifecycle.
  - Commands encapsulate user intent without controlling time.

- State-driven termination:
  The system does not exit based on loop conditions.
  Instead, termination or halting behavior is controlled through explicit
  system states such as STOPPED.

This structure allows the same control loop to be reused for:
- Automated tests
- Simulations
- Future real-time or event-based integrations
"""

#메인으로 실행할 프로그램

import time
from src.controller.telescope import Telescope
from src.controller.command_manager import CommandManager
from src.controller.command import MoveCommand, StopCommand
from src.utils.logger import log

def main():
    dt = 0.1

    telescope = Telescope()
    manager = CommandManager()

    # 시나리오 등록
    manager.add_command(MoveCommand(10, 10))
    manager.add_command(MoveCommand(20, 20))
    manager.add_command(StopCommand())

    log("[SYSTEM] Telescope control system started.")
    
    # Main control loop (system stays alive and waits for commands)
    while True:
        telescope.update(dt)
        manager.update(telescope, dt)
        time.sleep(dt)

if __name__ == "__main__":
    main()
