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
import json
from src.controller.telescope import Telescope
from src.controller.command_manager import CommandManager
from src.controller.command import MoveCommand, StopCommand
from src.scheduler.scheduler import SystemController
from src.utils.logger import log
from src.sim.remote_gate import RemoteCommandGate

def main():
    dt = 0.1

    telescope_a = Telescope()
    manager_a = CommandManager("A", telescope_a)

    telescope_b = Telescope()
    manager_b = CommandManager("B", telescope_b)

    system = SystemController()
    system.register_manager("A", manager_a)
    system.register_manager("B", manager_b)

    # 시나리오 등록
    manager_a.add_command(MoveCommand(5, 5))
    manager_b.add_command(MoveCommand(10, 10))
    #manager_a.add_command(StopCommand())

    log("[SYSTEM] Multi-Telescope control system started.")
    
    # Main control loop (system stays alive and waits for commands)
    while True:
        system.update(dt)
        #manager.update(telescope, dt)
        time.sleep(dt)

if __name__ == "__main__":
    # 1. 시스템 초기화
    ctrl = SystemController()
    tel = Telescope()
    mgr = CommandManager("Main", tel)
    ctrl.register_manager("Main", mgr)
    gate = RemoteCommandGate(ctrl)

    print("=== Day 100 Demo System Ready ===")
    
    # 2. 시나리오 실행: 설정 변경 -> 이동 -> 에러 발생 -> 진단
    commands = [
        '{"action": "CONFIG_UPDATE", "params": {"slew_rate": 30.0}}',
        '{"action": "MOVE", "manager": "Main", "params": {"alt": 45.0, "az": 180.0}}',
        '{"action": "MOVE", "manager": "Main", "params": {"alt": -99, "az": 0}}', # 의도적 에러
        '{"action": "DIAGNOSTICS"}'
    ]

    for cmd in commands:
        result = gate.process_json_command(cmd)
        print(f"INPUT: {cmd[:50]}... -> RESULT: {result['status']}")

    print("=== Final Health Check ===")
    print(json.dumps(ctrl.get_diagnostics(), indent=2))