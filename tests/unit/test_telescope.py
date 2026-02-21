from src.controller.telescope import Telescope, EPSILON
from src.controller.enums import TelescopeState
import pytest

# ✅ Test 1: 목표 도달 테스트 (이미 도달한 경우)
def test_telescope_should_remain_idle_when_move_is_requested_at_current_position():
    t = Telescope()
    t.alt, t.az = 5.0, 5.0  # 현재 위치
    
    t.enqueue_move(5.0, 5.0) # 현재 위치와 동일한 목표
    t.update(0.1)
    
    # 결과: 움직이지 않고 즉시 IDLE 혹은 짧은 확인 후 IDLE
    assert t.state == TelescopeState.IDLE
    assert t.alt == 5.0
    assert t.az == 5.0

# ✅ Test 2: 이동 후 도달 테스트 (정상 궤적)
def test_telescope_should_reach_target_position_and_stop_within_epsilon():
    t = Telescope(slew_rate=2.0)
    t.alt, t.az = 0.0, 0.0
    
    target_alt, target_az = 1.0, 0.0
    t.enqueue_move(target_alt, target_az)
    
    # 충분한 시간 동안 업데이트 (가감속 로직 포함)
    for _ in range(100):
        t.update(0.1)
        if t.state == TelescopeState.IDLE:
            break
            
    assert t.state == TelescopeState.IDLE
    assert abs(t.alt - target_alt) < EPSILON
    assert t.v_alt == 0.0 # 정지 시 속도는 0이어야 함

# ✅ Test 3: STOP 래치 테스트 (정지 후 요지부동)
def test_telescope_should_maintain_stopped_state_and_freeze_position_after_stop():
    t = Telescope()
    t.enqueue_move(10.0, 10.0)
    
    t.update(0.1)
    assert t.state == TelescopeState.MOVING
    
    t.stop() # 긴급 정지
    assert t.state == TelescopeState.STOPPED
    
    frozen_alt = t.alt
    frozen_az = t.az
    
    # 정지 상태에서 시간이 흘러도 위치가 변하지 않아야 함
    for _ in range(10):
        t.update(0.1)
        
    assert t.alt == frozen_alt
    assert t.az == frozen_az
    assert t.state == TelescopeState.STOPPED

"""
1. Telescope는 정말 외부를 몰라도 되는가?
A: 몰라야 함   
    외부에 존재를 알게 되면 망원경이 아닌 특정 sw 전용 부품이 됨

2. stop()이 “상태 전이”인가 “물리 정지”인가?
A: 상태 정의가 유발하는 물리 정지
    state를 바꾸지 않고 물리량만 0으로 만들면 Commamd는 망원경이 왜 멈췄는지 알 수 없음

3. STOPPED 상태에서 move_to를 허용해야 하는가?
A: NO
    STOPPED는 긴급이나 점검 상황을 의미하기 때문에 move_to를 허용하면 STOP의 의미가 없음
"""