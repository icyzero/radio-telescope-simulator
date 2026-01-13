import matplotlib.pyplot as plt
from src.controller.telescope import Telescope

dt = 0.1  # 고정 시간 간격 (s)
sim_time = 60  # 총 시뮬레이션 시간 (s)

telescope = Telescope(slew_rate=2.0)

# 기록용 배열
times = []
alts = []
azs = []

telescope.move_to(10, 10)
telescope.move_to(20, 20)
telescope.move_to(30, 30)

current_time = 0.0

while current_time <= sim_time:
    telescope.update(dt)

    times.append(current_time)
    alts.append(telescope.alt)
    azs.append(telescope.az)

    current_time += dt

plt.figure()
plt.plot(times, alts, label="Altitude")
plt.plot(times, azs, label="Azimuth")
plt.xlabel("Time (s)")
plt.ylabel("Angle (deg)")
plt.title("Telescope Motion Over Time")
plt.legend()
plt.grid()
plt.show()

plt.figure()
plt.plot(azs, alts, marker='o', markersize=2)
plt.xlabel("Azimuth (deg)")
plt.ylabel("Altitude (deg)")
plt.title("Telescope Trajectory (Az vs Alt)")
plt.grid()
plt.show()
