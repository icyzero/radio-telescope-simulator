import matplotlib.pyplot as plt
from src.controller.telescope import Telescope

dt = 0.1  # 0.1초마다 업데이트
sim_time = 60  # 총 60초 동안 실행

telescope = Telescope(slew_rate=2.0) # 망원경 객체 생성 (최대속도는 2°/초)

# 기록용 배열
times = []
alts = []
azs = []

telescope.move_to(10, 10)
telescope.move_to(20, 20)
telescope.move_to(30, 30)

current_time = 0.0

while current_time <= sim_time: #while문으로 움직임 업데이트
    telescope.update(dt)#0.1초마다 업데이트

    times.append(current_time) #시간흐름
    alts.append(telescope.alt) #고도변화
    azs.append(telescope.az)   #방위각변화

    current_time += dt

plt.figure()#새로운 그래프 창 생성
plt.plot(times, alts, label="Altitude")# 시간(times)을 x축, 고도(alts)를 y축으로 선 그래프를 그림
plt.plot(times, azs, label="Azimuth")# 같은 x축을 공유하면서 방위각(azs) 데이터도 선 그래프로 추가
plt.xlabel("Time (s)")# x축 이름을 "Time (s)" 로 지정 (단위가 초라는 의미)
plt.ylabel("Angle (deg)")# y축 이름을 "Angle (deg)" 로 지정 (각도가 단위라는 뜻)
plt.title("Telescope Motion Over Time")# 그래프 제목 설정
plt.legend()# 위 두 plot의 label을 사용하여 범례(어떤 선이 고도인지, 방위각인지)를 표시
plt.grid()# 그래프에 격자선 추가 (값 읽기 편하게 하기 위해)
plt.show()# 지금까지 설정한 그래프를 화면에 출력

plt.figure()
plt.plot(azs, alts, marker='o', markersize=2)# x축에 방위각(azs), y축에 고도(alts)를 찍으며 이동 경로를 그림
                                             # marker='o'는 점을 ○ 모양으로 찍겠다는 뜻
                                             # markersize=2는 점 크기를 2로 작게 설정
plt.xlabel("Azimuth (deg)")
plt.ylabel("Altitude (deg)")
plt.title("Telescope Trajectory (Az vs Alt)")
plt.grid()
plt.show()
