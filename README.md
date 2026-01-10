# Radio Telescope Control Simulator

This project is a Python-based simulator for controlling a radio telescope.
The goal is to model telescope motion, scheduling, and observation control.
This repository is part of my preparation for graduate studies in radio astronomy software.


Day 2: Implemented error-based convergence check and automated test

Day 3: Added smooth deceleration + precise target lock-in (all tests passing).

Day 4: Added command queue processing with sequential target execution (multi-target tests passing).

day 6: telescope의 동작 : “외부에서 move_to(x)를 호출하면 Telescope는 목표 좌표를 설정하고 MOVING 상태가 되며, 이후 update()가 반복 호출되면서 현재 위치(alt, az)가 목표 위치 방향으로 점진적으로 변하고, distance < EPSILON 조건이 만족되면 이동을 종료하고 IDLE 상태로 돌아간다.” & 로그 정리