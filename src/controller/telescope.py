# src/controller/telescope.py
import math

EPSILON = 0.1 #목표 도달로 판단하는 최소 각도 오차(도)
STATE_IDLE = "IDLE"
STATE_MOVING = "MOVING"
STATE_STOPPED = "STOPPED"

class Telescope:
    def __init__(self, slew_rate=2.0):
        """slew_rate : degrees per second"""

        self.alt = 0.0 #현재 고도
        self.az = 0.0 #현제 방위각

        self.target_alt = None#목표 고도
        self.target_az = None#목표 방위각

        self.alt_error = 0.0 #01.06 고도 오류 제어
        self.az_error = 0.0 #01.06 방위각 오류 제어

        self.slew_rate = slew_rate#움직임 속도
        self.state = STATE_IDLE # 사용 중 상태: IDLE, MOVING, STOPPED

        self.command_queue = [] #01.08 명령을 여러 개 받아 수행하기 위한 배열

    def move_to(self, alt, az):
        '''self.target_alt = alt
        self.target_az = az
        self.state = "MOVING"'''#01.08 주석 처리 / 바로 이동이 아닌 큐에 저장하기 위해서
        self.command_queue.append((alt, az)) #01.08 바로 이동이 아닌 큐에 저장
        print(f"[COMMAND] Move to Alt={alt}, Az={az}")

    def stop(self):
        self.state = STATE_STOPPED
        self.target_alt = None
        self.target_az = None
        self.command_queue.clear()  # 01.08 큐 비우기
        print(f"[STATE] → {STATE_STOPPED} (force stop)")#01.10 로그 정리

    def update(self, dt):
        """dt : 초마다 시간 경과"""

        if self.state == STATE_STOPPED: # 01.10 STOPPED상태를 적용함 / 정지 상태면 아무 것도 안함
            return

        if self.state != STATE_MOVING: # 01.08 현재 이동 중이면 update, 아니라면 큐에서 다음 명령 꺼내기 #01.10 로그 정리
            if self.command_queue:
                self.target_alt, self.target_az = self.command_queue.pop(0)
                self.state = STATE_MOVING
                print(f"[STATE] {STATE_IDLE} → {STATE_MOVING} "
                  f"(Alt={self.target_alt}, Az={self.target_az})")#01.10 로그 정리
            else:
                return
        
        d_alt = self.target_alt - self.alt #목표 고도까지 남은 거리
        d_az = self.target_az - self.az    #목표 방위각까지 남은 거리
        distance = math.sqrt(d_alt**2 + d_az**2)#목표까지 남은 거리 계산 피타고라스정리 활용

        if distance < EPSILON: #01.07 멈추는 조건을 EPSILON과 맞추기 / 거리가 EPSILON보다 작으면 상태 IDLE로 변환
            self.alt = self.target_alt
            self.az = self.target_az
            self.state = STATE_IDLE
            print(f"[STATE] {STATE_MOVING} → {STATE_IDLE} (target reached)")#01.10 로그 정리
            return
        
        step = self.slew_rate * dt * (distance/10)#01.07 목표까지 남은 거리만큼 속도 줄이기 (100은 너무 큼) / 이번 dt동안 움직일 최대 거리 / 기본 이동량 = slew_rate * dt & 남은 거리에 비례해서 가감속 = (distance / 10)
        ratio = min(step / distance, 1.0)#남은 거리 중 얼만큼 이동할지 비율 / 전체 거리 대비 이동량 비율 = step / distance & 과하게 튀어나가지 않도록 제한 = min(..., 1.0)
        #print(f"dist={distance:.2f}")#01.07 거리가 줄어드는 것 확인 (코드 삭제해도 상관없음)
            
        self.alt += d_alt * ratio #목표 고도로 ratio만큼 이동
        self.az += d_az * ratio   #목표 방위각으로 ratio만큼 이동

        print(f"[UPDATE] state={self.state} "
                f"Alt={self.alt:.2f}, Az={self.az:.2f}")#01.10 로그 정리

        #01.06 지금 위치가 목표에서 얼마나 벗어나 있는지
        self.alt_error = self.target_alt - self.alt #목표 고도 - 현재 고도
        self.az_error = self.target_az - self.az #목표 방위각 - 현재 방위각

        #01.07 오차로도 도달 판단 + 보정 + 정지
        '''if abs(self.alt_error) < EPSILON and abs(self.az_error) < EPSILON:
            self.alt = self.target_alt
            self.az = self.target_az
            self.state = "IDLE"
            print("[STATE] Target reached (epsilon)")
            return'''
        
        #print(f"[UPDATE] Alt={self.alt:.2f},Az={self.az:.2f}")


    #01.06 상태 체크용
    def is_target_reached(self):
        return(
            abs(self.alt_error) < EPSILON and
            abs(self.az_error) < EPSILON
        )