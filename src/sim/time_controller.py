# src/sim/time_controller.py

import time

class TimeController:
    def __init__(self, scale: float = 1.0):
        self.scale = scale
        self.origin_wall = time.time()
        self.origin_sim = 0.0

    def get_sim_time(self) -> float:
        """현재 가속된 시뮬레이션 시간을 반환"""
        elapsed_wall = time.time() - self.origin_wall
        return self.origin_sim + (elapsed_wall * self.scale)

    def set_scale(self, new_scale: float):
        """배속을 변경할 때 현재 시뮬레이션 시간을 고정하고 기준점을 갱신"""
        # 1. 현재 시점의 '벽시계 시간'을 딱 한 번만 캡처합니다.
        now_wall = time.time()
        
        # 2. 이 시점까지의 시뮬레이션 시간을 계산 (기존 scale 적용)
        elapsed_wall = now_wall - self.origin_wall
        current_sim = self.origin_sim + (elapsed_wall * self.scale)
        
        # 3. 기준점들을 동시에 갱신
        self.origin_sim = current_sim
        self.origin_wall = now_wall
        self.scale = new_scale
        
        # print(f"[Time] Scale changed to x{new_scale}. Current Sim Time: {current_sim:.2f}s")