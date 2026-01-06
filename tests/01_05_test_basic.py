import time
from src.controller.telescope import Telescope

telescope = Telescope(slew_rate=5.0)
telescope.move_to(30, 120)

for _ in range(20):
    telescope.update(dt=0.5)
    time.sleep(0.5)
