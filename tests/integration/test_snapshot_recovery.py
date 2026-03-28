# tests/integration/test_snapshot_recovery.py

import pytest
from src.scheduler.scheduler import SystemController
from src.sim.snapshot_manager import SnapshotManager
from src.sim.event_replayer import EventReplayer
from src.sim.event import Event, EventType

def test_snapshot_hybrid_recovery_consistency():
    # --- STEP 1: 원본 시스템 실행 (이벤트 100개 발생 가정) ---
    sys_original = SystemController()
    sys_original.resume()
    
    # 예시 이벤트 스트림 생성 (0~99번)
    events = []
    for i in range(100):
        # 각 이벤트는 고유 ID를 가져야 추적이 편합니다.
        e = Event(EventType.COMMAND_STARTED, "Mgr", {"idx": i}, sim_time=float(i), id=i)
        events.append(e)
    
    # 0~49번까지만 먼저 실행
    EventReplayer.replay(sys_original, events[:50])
    
    # --- STEP 2: 중간 지점(50번 직후) 스냅샷 캡처 ---
    # 49번 이벤트까지 처리된 상태를 저장
    checkpoint_snap = SnapshotManager.capture(sys_original, last_event_id=49)
    
    # 나머지 50~99번 실행해서 최종 상태 도달
    EventReplayer.replay(sys_original, events[50:])
    final_state_original = sys_original.get_full_state() # 전체 상태 추출 가정

    # --- STEP 3: 하이브리드 복원 시스템 가동 ---
    sys_recovered = SystemController()
    
    # 스냅샷 주입 (50번 시점으로 워프!)
    sys_recovered.set_full_state(checkpoint_snap) 
    
    # 스냅샷 이후의 이벤트(50~99번)만 Replay
    remaining_events = [e for e in events if e.id > checkpoint_snap["last_event_id"]]
    EventReplayer.replay(sys_recovered, remaining_events)
    
    # --- STEP 4: 최종 비교 ---
    assert sys_recovered.get_full_state() == final_state_original