# src/controller/telescope.py
import math
from controller.command import Command

EPSILON = 0.1 #목표 도달로 판단하는 최소 각도 오차(도)
STATE_IDLE = "IDLE"
STATE_MOVING = "MOVING"
STATE_STOPPED = "STOPPED"

STOP_NONE = None #01.15
STOP_OVERSHOOT = "OVERSHOOT" #목표보다 많이 넘어감
STOP_STALL = "STALL" #속도가 0에 가까운데 거리가 큼
STOP_MANUAL = "MANUAL" #외무에서 stop()호출

class Telescope:
    def __init__(self, slew_rate=2.0):
        """slew_rate : degrees per second"""

        self.alt = 0.0 #현재 고도
        self.az = 0.0 #현제 방위각

        #self.target_alt = None#목표 고도
        #self.target_az = None#목표 방위각

        self.alt_error = 0.0 #01.06 고도 오류 제어
        self.az_error = 0.0 #01.06 방위각 오류 제어

        self.slew_rate = slew_rate#움직임 속도
        self.state = STATE_IDLE # 사용 중 상태: IDLE, MOVING, STOPPED

        self.v_alt = 0.0#01.12 고도 움직이는 속도[altitude velocity](deg/s)
        self.v_az = 0.0#01.12 방위각 움직이는 속도[azimuth velocity](deg/s)

        self.MAX_SPEED = 2.0 #01.14 실제 모터에는 최대 속도가 있음
        self.MIN_SPEED = 0.1 #01.14 목표 근처에서는 아주 느리게라도 끝까지 이동

        self.current_command = None #01.16 실행중인 명령을 객체로 분리
        self.command_queue = [] #01.08 명령을 여러 개 받아 수행하기 위한 배열

        self.stop_reason = STOP_NONE

    def move_to(self, alt, az, execute_at=None):
        '''self.target_alt = alt
        self.target_az = az
        self.state = "MOVING"'''#01.08 주석 처리 / 바로 이동이 아닌 큐에 저장하기 위해서
        self.command_queue.append(Command(alt, az, execute_at)) #01.08 바로 이동이 아닌 큐에 저장
        print(f"[COMMAND] Move to Alt={alt}, Az={az}")

    def stop(self, reason=STOP_MANUAL):
        self.state = STATE_STOPPED
        self.stop_reason = reason #01.15
        '''self.target_alt = None
        self.target_az = None'''
        self.command_queue.clear()  # 01.08 큐 비우기
        print(f"[STATE] → {STATE_STOPPED} (force stop)")#01.10 로그 정리

    def cancel_all(self): #01.16 큐만 지우는 동작
        self.command_queue.clear()

    def skip_current(self): #01.16 현재 명령만을 포기하고 다음 update()에서 자동으로 다음 큐 명영으로 진입
        self.current_command = None
        self.state = STATE_IDLE

    def get_status(self):
        return {
            "state": self.state,
            "current": self.current_command,
            "queue_length": len(self.command_queue),
            "stop_reason": self.stop_reason
        }


    def update(self, dt):
        """dt : 초마다 시간 경과"""

        if self.state == STATE_STOPPED: # 01.10 STOPPED상태를 적용함 / 정지 상태면 아무 것도 안함
            return

        if self.state != STATE_MOVING: # 01.08 현재 이동 중이면 update, 아니라면 큐에서 다음 명령 꺼내기 #01.10 로그 정리
            if self.current_command is None and self.command_queue:
                self.current_command = self.command_queue.pop(0)
                self.state = STATE_MOVING
                target_alt = self.current_command.alt
                target_az = self.current_command.az #어디로 가기 시작했는지
                print(f"[STATE] {STATE_IDLE} → {STATE_MOVING} "
                  f"(Alt={target_alt}, Az={target_az})")#01.10 로그 정리
            else:
                return

        if self.state in(STATE_IDLE,STATE_STOPPED): #01.12 멈춰있으면 속도는 0 / Day 8: position is updated via velocity, not directly controlled
            self.v_alt = 0.0
            self.v_az = 0.0
        
        target_alt = self.current_command.alt
        target_az = self.current_command.az #지금 어디를 향해 움직이는지
        
        d_alt = target_alt - self.alt #목표 고도까지 남은 거리
        d_az = target_az - self.az    #목표 방위각까지 남은 거리
        distance = math.sqrt(d_alt**2 + d_az**2)#목표까지 남은 거리 계산 피타고라스정리 활용

        if distance < EPSILON: #01.07 멈추는 조건을 EPSILON과 맞추기 / 거리가 EPSILON보다 작으면 상태 IDLE로 변환
            self.alt = target_alt
            self.az = target_az
            self.v_alt = 0.0 #도착시 속도 0으로
            self.v_az = 0.0 #도착시 속도 0으로
            self.current_command = None
            self.state = STATE_IDLE
            print(f"[STATE] {STATE_MOVING} → {STATE_IDLE} (target reached)")#01.10 로그 정리
            return
        
        #방향 백처 계산
        dir_alt = d_alt / distance #이동방향 정규화 / 01.12 위치 수정 방향 백터 계산 전에 도착 여부 먼저 판단(이유 distance==0이면 오류 발생방지)
        dir_az = d_az / distance #이동방향 정규화 / 01.12 위치 수정 방향 백터 계산 전에 도착 여부 먼저 판단

        #속도 크기 계산
        raw_speed = self.slew_rate * (distance/10)
        speed = min(max(raw_speed,self.MIN_SPEED),self.MAX_SPEED) #01.14 모터가 움직일 수 있는 최대 속도보다 빠르지 않게, 목표에 가까워질 때 0이아닌 최소 속도로 목표에 도달하게끔

        #velocity 계산
        self.v_alt = dir_alt * speed #고도 속도 설정
        self.v_az = dir_az * speed #방위각 속도 설정

        #위치 갱신
        self.alt += self.v_alt * dt #속도로 고도 위치 갱신
        self.az += self.v_az * dt #속도로 방위각 위치 갱신
        
        '''step = self.slew_rate * dt * (distance/10)#01.07 목표까지 남은 거리만큼 속도 줄이기 (100은 너무 큼) / 이번 dt동안 움직일 최대 거리 / 기본 이동량 = slew_rate * dt & 남은 거리에 비례해서 가감속 = (distance / 10)
        ratio = min(step / distance, 1.0)#남은 거리 중 얼만큼 이동할지 비율 / 전체 거리 대비 이동량 비율 = step / distance & 과하게 튀어나가지 않도록 제한 = min(..., 1.0)
        #print(f"dist={distance:.2f}")#01.07 거리가 줄어드는 것 확인 (코드 삭제해도 상관없음)
            
        self.alt += d_alt * ratio #목표 고도로 ratio만큼 이동
        self.az += d_az * ratio   #목표 방위각으로 ratio만큼 이동'''

        print(f"[UPDATE] state={self.state} "
                f"Alt={self.alt:.2f}, Az={self.az:.2f}")#01.10 로그 정리

        #01.06 지금 위치가 목표에서 얼마나 벗어나 있는지
        self.alt_error = target_alt - self.alt #목표 고도 - 현재 고도
        self.az_error = target_az - self.az #목표 방위각 - 현재 방위각

        #01.07 오차로도 도달 판단 + 보정 + 정지
        '''if abs(self.alt_error) < EPSILON and abs(self.az_error) < EPSILON:
            self.alt = self.target_alt
            self.az = self.target_az
            self.state = "IDLE"
            print("[STATE] Target reached (epsilon)")
            return'''     
        #print(f"[UPDATE] Alt={self.alt:.2f},Az={self.az:.2f}")

    def can_resume(self): #01.15일단 설계만
        return self.state == STATE_STOPPED and self.stop_reason != STOP_OVERSHOOT



    #01.06 상태 체크용
    def is_target_reached(self):
        return(
            abs(self.alt_error) < EPSILON and
            abs(self.az_error) < EPSILON
        )