# tests/integration/test_replay_determinism.py

import pytest
from src.scheduler.scheduler import SystemController
from src.sim.event_replayer import EventReplayer
from src.sim.event_types import EventType
from src.utils.state_helper import capture_system_state

def test_replay_determinism():
    # 1. 원본 시스템 설정 및 동작
    system = SystemController()
    # 필요하다면 여기서 실제 매니저를 등록할 수 있습니다.
    
    system.resume() # NORMAL 모드로 변경
    system.pause()  # PAUSED 모드로 변경
    
    # 2. 실행 직후 상태 캡처
    state_before = capture_system_state(system)
    events = system.bus.get_events()

    # 3. 새로운 시스템 생성 (완전 초기 상태)
    new_system = SystemController()
    
    # 4. 리플레이 실행 (상태 강제 복원)
    EventReplayer.replay(new_system, events)
    
    # 5. 결정론적 재현 검증 (Before == After)
    state_after = capture_system_state(new_system)
    
    assert state_before == state_after
    print("\n[SUCCESS] Determinism Verified: State before and after replay are identical.")