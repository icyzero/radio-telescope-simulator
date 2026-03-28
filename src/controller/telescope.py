# src/controller/telescope.py
import math
from src.controller.enums import TelescopeState

from src.utils.logger import log

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

        self.target_alt = 0.0#목표 고도
        self.target_az = 0.0#목표 방위각

        self.alt_error = 0.0 #01.06 고도 오류 제어
        self.az_error = 0.0 #01.06 방위각 오류 제어

        self.slew_rate = slew_rate#움직임 속도
        self.state = TelescopeState.IDLE # 사용 중 상태: IDLE, MOVING, STOPPED

        self.v_alt = 0.0#01.12 고도 움직이는 속도[altitude velocity](deg/s)
        self.v_az = 0.0#01.12 방위각 움직이는 속도[azimuth velocity](deg/s)

        self.MAX_SPEED = 2.0 #01.14 실제 모터에는 최대 속도가 있음
        self.MIN_SPEED = 0.1 #01.14 목표 근처에서는 아주 느리게라도 끝까지 이동

        self.current_command = None #01.16 실행중인 명령을 객체로 분리
        self.command_queue = [] #01.08 명령을 여러 개 받아 수행하기 위한 배열

        self.stop_reason = STOP_NONE

    def move_to(self, alt, az):
        '''self.target_alt = alt
        self.target_az = az
        self.state = "MOVING"'''#01.08 주석 처리 / 바로 이동이 아닌 큐에 저장하기 위해서
        self.command_queue.append((alt, az)) #01.08 바로 이동이 아닌 큐에 저장
        print(f"[COMMAND] Move to Alt={alt}, Az={az}")

    def stop(self, reason=STOP_MANUAL):
        self.state = TelescopeState.STOPPED
        self.stop_reason = reason #01.15
        '''self.target_alt = None
        self.target_az = None'''
        self.command_queue.clear()  # 01.08 큐 비우기
        print(f"[STATE] → {STATE_STOPPED} (force stop)")#01.10 로그 정리

    def cancel_all(self): #01.16 큐만 지우는 동작
        self.command_queue.clear()

    def skip_current(self): #01.16 현재 명령만을 포기하고 다음 update()에서 자동으로 다음 큐 명영으로 진입
        self.current_command = None
        self.state = TelescopeState.IDLE

    def get_status(self):
        return {
            "state": self.state,
            "current": self.current_command,
            "queue_length": len(self.command_queue),
            "stop_reason": self.stop_reason
        }
    
    def enqueue_move(self, alt, az): #command.py 창구 메서드 이동 좌표만 저장
        """Manager/Command로부터 새로운 단일 목표를 수신"""
        self.target_alt = alt # 💡 여기서 저장해줘야 update가 알 수 있습니다.
        self.target_az = az
        self.state = TelescopeState.MOVING
        
        # 물리 계산을 위해 current_command 형식도 유지 (기존 로직 호환성)
        self.current_command = (alt, az)
        
        log(f"[STATE] IDLE → MOVING (Target: {alt}, {az})")

    def update(self, dt):
        """dt : 초마다 시간 경과"""

        if self.state == TelescopeState.STOPPED: # 01.10 STOPPED상태를 적용함 / 정지 상태면 아무 것도 안함
            return
        
        if self.state != TelescopeState.MOVING or self.current_command is None:
            # 큐에서 다음 명령을 꺼내는 기존 로직 (Manager 없이 직접 쓸 때를 대비)
            if self.command_queue:
                self.current_command = self.command_queue.pop(0) # 가장 오래 기다린 명령 현재 작업으로 설정
                self.target_alt, self.target_az = self.current_command # 좌표 묶음을 alt, az 각각 분리 저장
                self.state = TelescopeState.MOVING #MOVIG으로 상태 변경
            else:
                return
            
        # 1. 물리 계산 준비
        target_alt, target_az = self.current_command #지금 어디를 향해 움직이는지
        d_alt = target_alt - self.alt #목표 고도까지 남은 거리
        d_az = target_az - self.az    #목표 방위각까지 남은 거리
        distance = math.sqrt(d_alt**2 + d_az**2)#목표까지 남은 거리 계산 피타고라스정리 활용

        #2. 도착 판정(도착 시 위치 고정 및 정지)
        if distance < EPSILON: #01.07 멈추는 조건을 EPSILON과 맞추기 / 거리가 EPSILON보다 작으면 상태 IDLE로 변환
            self.alt = target_alt
            self.az = target_az
            self.v_alt = 0.0 #도착시 속도 0으로
            self.v_az = 0.0 #도착시 속도 0으로
            self.current_command = None
            self.state = TelescopeState.IDLE
            print(f"[STATE] {STATE_MOVING} → {STATE_IDLE} (Target Reached)")#01.10 로그 정리
            return
        
        #3. 속도 및 방향 개선
        dir_alt = d_alt / distance #이동방향 정규화 / 01.12 위치 수정 방향 백터 계산 전에 도착 여부 먼저 판단(이유 distance==0이면 오류 발생방지)
        dir_az = d_az / distance #이동방향 정규화 / 01.12 위치 수정 방향 백터 계산 전에 도착 여부 먼저 판단

        # 1️⃣속도 크기 계산(거리에 비례하되 MAX/MIN 제한)
        raw_speed = self.slew_rate * (distance/10)
        speed = min(max(raw_speed, self.MIN_SPEED), self.MAX_SPEED) #01.14 모터가 움직일 수 있는 최대 속도보다 빠르지 않게, 목표에 가까워질 때 0이아닌 최소 속도로 목표에 도달하게끔

        # 4. 💡 방어 설계: 이번 프레임의 이동량이 남은 거리보다 크면 바로 도착 처리 (Clamping)
        # 2️⃣ 이번 틱에 사용할 속도 업데이트
        self.v_alt = dir_alt * speed
        self.v_az = dir_az * speed

        # 3️⃣ 💡 방어 설계: 계산된 v_alt를 사용하여 이동량 확인
        move_alt = self.v_alt * dt
        move_az = self.v_az * dt
        
        move_dist = math.sqrt(move_alt**2 + move_az**2)# 실제 이동 시뮬레이션 거리
        
        if move_dist >= distance:
            self.alt = target_alt
            self.az = target_az
            self.v_alt = 0.0
            self.v_az = 0.0
            self.current_command = None
            self.state = TelescopeState.IDLE
            print(f"[STATE] MOVING → IDLE (Clamped to Target)")
        else:
            self.alt += move_alt
            self.az += move_az

        #01.06 지금 위치가 목표에서 얼마나 벗어나 있는지 (에러 업데이트)
        self.alt_error = target_alt - self.alt #목표 고도 - 현재 고도
        self.az_error = target_az - self.az #목표 방위각 - 현재 방위각

    def can_resume(self): #01.15일단 설계만
        return self.state == TelescopeState.STOPPED and self.stop_reason != STOP_OVERSHOOT

    def is_stopped(self): #01.29 Command에서 ABORTED를 활용하기 위해
        return self.state == TelescopeState.STOPPED

    #01.06 상태 체크용
    def is_target_reached(self):
        return(
            abs(self.alt_error) < EPSILON and
            abs(self.az_error) < EPSILON
        )
    
    # [Day 83] Snapshot 저장을 위한 메서드
    def get_state(self) -> dict:
        """시스템 복구를 위한 모든 내부 상태값 추출"""
        return {
            "alt": self.alt,
            "az": self.az,
            "target_alt": self.target_alt,
            "target_az": self.target_az,
            # Enum 객체는 JSON 저장이 안 되므로 value(문자열/숫자)로 변환
            "state": self.state.value if hasattr(self.state, 'value') else self.state,
            "v_alt": self.v_alt,
            "v_az": self.v_az,
            "current_command": self.current_command, # (alt, az) 튜플 형태
            "command_queue": list(self.command_queue), # 큐 복사
            "stop_reason": self.stop_reason
        }

    # [Day 83] Snapshot 로드를 위한 메서드
    def set_state(self, state_data: dict):
        """저장된 데이터를 바탕으로 망원경 상태 강제 복구"""
        self.alt = state_data["alt"]
        self.az = state_data["az"]
        self.target_alt = state_data["target_alt"]
        self.target_az = state_data["target_az"]
        
        # 다시 Enum 객체로 복원 (문자열 -> Enum)
        if isinstance(state_data["state"], str):
             # TelescopeState가 Enum이라면 값을 찾아 매핑
             self.state = TelescopeState(state_data["state"])
        else:
             self.state = state_data["state"]

        self.v_alt = state_data["v_alt"]
        self.v_az = state_data["v_az"]
        self.current_command = state_data["current_command"]
        self.command_queue = state_data["command_queue"]
        self.stop_reason = state_data["stop_reason"]
        
        # 물리 오차 다시 계산
        self.alt_error = self.target_alt - self.alt
        self.az_error = self.target_az - self.az