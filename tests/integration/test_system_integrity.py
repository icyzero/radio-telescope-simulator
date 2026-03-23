# tests/integration/test_system_integrity.py

import pytest
# 1. 정의되지 않았던 클래스들을 임포트합니다.
from src.scheduler.scheduler import SystemController
from src.sim.event_replayer import EventReplayer
from src.sim.event_persistence import EventPersistence # 저장/불러오기 필요 시

def test_full_replay_integrity(tmp_path):
    
    # 2. 시스템 컨트롤러 생성
    system = SystemController()
    
    # 3. (가정) 만약 TelescopeManager가 구현되어 있다면 임포트해서 등록
    # 지금은 테스트용 모크(Mock)나 간단한 매니저를 등록한다고 가정합니다.
    # system.register_manager("A", SomeManager()) 

    # 4. 시뮬레이션 동작 수행 (기록 생성)
    system.pause()
    system.resume()
    system.pause()
    
    # [중요] 현재 상태 스냅샷 저장 (원본)
    # 아직 get_full_state_snapshot이 없다면 system.mode 등으로 직접 비교
    original_mode = system.mode
    original_sim_time = system.sim_time
    events = system.bus.get_events() # 발생한 모든 이벤트 가져오기

    # ---------------------------------------------------------
    # 5. 완전히 새로운 시스템 객체 생성 (기억이 없는 상태)
    # ---------------------------------------------------------
    new_system = SystemController()
    assert new_system.mode == "NORMAL" # 초기 상태 확인
    
    # 6. 리플레이 실행 (상태 복원)
    EventReplayer.replay(new_system, events)
    
    # ---------------------------------------------------------
    # 7. 검증: 새 시스템이 과거의 상태를 완벽히 복원했는가?
    # ---------------------------------------------------------
    assert new_system.mode == original_mode
    assert new_system.sim_time == original_sim_time
    # 매니저가 있다면 매니저 상태도 비교합니다.