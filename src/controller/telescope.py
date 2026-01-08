# src/controller/telescope.py
import math

EPSILON = 0.1 #Degrees

class Telescope:
    def __init__(self, slew_rate=2.0):
        """slew_rate : degrees per second"""

        self.alt = 0.0
        self.az = 0.0

        self.alt_step = 0.6 #01.06
        self.az_step  = 2.4 #01.06

        self.target_alt = None
        self.target_az = None

        self.alt_error = 0.0 #01.06 고도 오류 제어
        self.az_error = 0.0 #01.06 방위각 오류 제어

        self.slew_rate = slew_rate
        self.state = "IDLE"

        self.command_queue = [] #01.08 명령을 여러 개 받아 수행하기 위한 배열

    def move_to(self, alt, az):
        '''self.target_alt = alt
        self.target_az = az
        self.state = "MOVING"'''#01.08 주석 처리 바로 이동이 아닌 큐에 저장하기 위해서
        self.command_queue.append((alt, az)) #01.08 바로 이동이 아닌 큐에 저장
        print(f"[COMMAND] Move to Alt={alt}, Az={az}")

    def stop(self):
        self.state = "STOPPED"
        self.target_alt = None
        self.target_az = None
        self.command_queue.clear()  # 01.08 큐 비우기
        print("[COMMAND] Stop")

    def update(self, dt):
        """dt : time step in seconds"""

        if self.state != "MOVING": # 01.08 현재 디옫중이면 update, 아니라면 큐에서 다음 명령 꺼내기
            if self.command_queue:
                self.target_alt, self.target_az = self.command_queue.pop(0)
                self.state = "MOVING"
                print(f"[START] Move to Alt={self.target_alt}, Az={self.target_az}")
            else:
                return
        
        d_alt = self.target_alt - self.alt
        d_az = self.target_az - self.az

        distance = math.sqrt(d_alt**2 + d_az**2)

        if distance < EPSILON: #01.07 멈추는 조건을 EPSILON과 맞추기
            self.alt = self.target_alt
            self.az = self.target_az
            self.state = "IDLE"
            print("[STATE] Target reached")
            return
        
        step = self.slew_rate * dt * (distance/10)#01.07 목표까지 남은 거리만큼 속도 줄이기 (100은 너무 큼)
        ratio = min(step / distance, 1.0)
        print(f"dist={distance:.2f}")#01.07 거리가 줄어드는 것 확인 (코드 삭제해도 상관없음)
            
        self.alt += d_alt * ratio
        self.az += d_az * ratio

        print(f"[UPDATE] Alt={self.alt:.2f},Az={self.az:.2f}")

        #01.06 지금 위치가 목표에서 얼마나 벗어나 있는지
        self.alt_error = self.target_alt - self.alt #목표 고도 - 현재 고도
        self.az_error = self.target_az - self.az #목표 방위각 - 현재 방위각

        #01.07 오차로도 도달 판단 + 보정 + 정지
        if abs(self.alt_error) < EPSILON and abs(self.az_error) < EPSILON:
            self.alt = self.target_alt
            self.az = self.target_az
            self.state = "IDLE"
            print("[STATE] Target reached (epsilon)")
            return
        
        print(f"[UPDATE] Alt={self.alt:.2f},Az={self.az:.2f}")


    #01.06
    def is_target_reached(self):
        return(
            abs(self.alt_error) < EPSILON and
            abs(self.az_error) < EPSILON
        )