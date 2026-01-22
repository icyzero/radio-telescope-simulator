# Radio Telescope Control Simulator

This project is a Python-based simulator for controlling a radio telescope.
The goal is to model telescope motion, scheduling, and observation control.
This repository is part of my preparation for graduate studies in radio astronomy software.


Day 2: Implemented error-based convergence check and automated test

Day 3: Added smooth deceleration + precise target lock-in (all tests passing).

Day 4: Added command queue processing with sequential target execution (multi-target tests passing).

day 6: telescope의 동작 : “외부에서 move_to(x)를 호출하면 Telescope는 목표 좌표를 설정하고 MOVING 상태가 되며, 이후 update()가 반복 호출되면서 현재 위치(alt, az)가 목표 위치 방향으로 점진적으로 변하고, distance < EPSILON 조건이 만족되면 이동을 종료하고 IDLE 상태로 돌아간다.” & 로그 정리

day 8: 위치 제어 → 속도 기반 제어로 개념 분리 시작

Day 9: Implemented time-based simulation loop and visualized telescope motion (Alt/Az vs time, trajectory).

Day 10: Validated velocity-constrained motion model with stable convergence under time-based simulation.

Day 11: Introduced explicit STOP reasons and structured error-state handling for telescope control.

Day 12: Extended command queue with runtime control (cancel, skip, status) for operational use.

Day 15: Project re-entry after illness; reviewed control flow and verified existing simulations without modification.

Day 16: Introduced time-aware command structure as a foundation for scheduling.

Day 17: command.py의 역할을 더 명확히 [Command는 사용자의 의도를 객체로 캡슐화해서 Telescope에 요청하는 역할]/ telescope.py원복(이유: telescope는 순수하게 움직이는 역할만 하기 위해) 

Day 18: Separate command lifecycle from telescope control and validate via tests
