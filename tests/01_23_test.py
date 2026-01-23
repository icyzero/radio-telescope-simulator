# command.py가 제대로 작동되는지 확인

from src.controller.command import MoveCommand
from src.controller.telescope import Telescope
import time

dt = 0.1
telescope = Telescope(slew_rate=0.05)

cmd = MoveCommand(100, 100)

cmd.timeout = 1.0

print("[CMD] MoveCommand START")
cmd.execute(telescope)

# Command 실행 중
while cmd.state == "RUNNING":
    telescope.update(dt)
    cmd.update(telescope, dt)
    time.sleep(dt)

# Command는 끝났지만, Telescope 정리 대기
while telescope.state != "IDLE":
    telescope.update(dt)
    time.sleep(dt)
