# tests/unit/test_time_scaling.py

import time
import pytest
from src.sim.time_controller import TimeController

def test_time_scaling_acceleration():
    tc = TimeController(scale=10.0) # 10배속
    
    start_sim = tc.get_sim_time()
    time.sleep(1.0) # 현실 시간 1초 대기
    end_sim = tc.get_sim_time()
    
    elapsed_sim = end_sim - start_sim
    
    # 현실 1초 동안 시뮬레이션은 약 10초 흘러야 함 (오차 범위 감안)
    assert 9.9 <= elapsed_sim <= 10.1

def test_scale_change_continuity():
    tc = TimeController(scale=1.0)
    time.sleep(0.5)
    
    time_before = tc.get_sim_time()
    tc.set_scale(100.0) # 갑자기 100배속으로 변경
    time_after = tc.get_sim_time()
    
    # 배속을 바꿔도 시간값이 튀지 않고 연속적이어야 함
    assert pytest.approx(time_before, abs=0.01) == time_after