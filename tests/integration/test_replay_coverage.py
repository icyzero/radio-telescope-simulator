# tests/integration/test_replay_coverage.py

import pytest
from src.scheduler.scheduler import SystemController
from src.sim.event_replayer import EventReplayer
from src.utils.state_helper import capture_system_state
from src.sim.event import Event, EventType

def test_full_scenario_replay():
    # 1. 복합 시나리오 구성
    sys = SystemController()
    sys.resume()
    
    # 임의로 이벤트를 발생시키는 시뮬레이션 동작 수행
    # (실제 매니저가 있다면 매니저 동작 포함)
    sys.pause()
    sys.resume()
    
    # 2. 상태 캡처 및 리플레이
    original_state = capture_system_state(sys)
    events = sys.bus.get_events()
    
    new_sys = SystemController()
    EventReplayer.replay(new_sys, events)
    
    # 3. 최종 검증
    restored_state = capture_system_state(new_sys)
    assert original_state == restored_state

def test_replay_multiple_commands():
    sys = SystemController()
    sys.resume() # 운용 모드 전환
    
    # 시나리오: 명령 A 시작 -> 성공 -> 명령 B 시작 -> 성공
    # (현재는 수동으로 이벤트를 찍어서 흐름을 시뮬레이션합니다)
    sys.bus.publish(Event(EventType.COMMAND_STARTED, "Mgr", {"cmd_type": "MOVE"}, 1.0))
    sys.bus.publish(Event(EventType.COMMAND_SUCCESS, "Mgr", {
        "cmd_type": "MOVE", 
        "result_state": {"manager_state": "IDLE", "queue_size": 0}
    }, 2.0))
    
    # 두 번째 명령
    sys.bus.publish(Event(EventType.COMMAND_STARTED, "Mgr", {"cmd_type": "TRACK"}, 3.0))
    sys.bus.publish(Event(EventType.COMMAND_SUCCESS, "Mgr", {
        "cmd_type": "TRACK", 
        "result_state": {"manager_state": "IDLE", "queue_size": 0}
    }, 4.0))

    # 검증
    events = sys.bus.get_events()
    new_sys = SystemController()
    EventReplayer.replay(new_sys, events)
    
    assert new_sys.mode == "NORMAL"
    # 매니저 상태 등 세부 검증...

# tests/integration/test_replay_coverage.py 수정 제안

def test_replay_with_failure():
    sys = SystemController()
    
    # [추가] 원본 시스템에 매니저 등록 (현실적인 환경 구축)
    # 실제 매니저 클래스가 없다면 딕셔너리에 직접 주입하거나 Mock을 사용합니다.
    from types import SimpleNamespace
    sys.managers["Mgr"] = SimpleNamespace(state="IDLE", command_queue=[])

    # 시나리오 실행 (동일)
    sys.bus.publish(Event(EventType.COMMAND_STARTED, "Mgr", {"cmd_type": "MOVE"}, 1.0))
    sys.bus.publish(Event(EventType.COMMAND_FAILED, "Mgr", {
        "cmd_type": "MOVE", 
        "reason": "Hardware Error",
        "result_state": {"manager_state": "IDLE", "queue_size": 0}
    }, 2.0))

    events = sys.bus.get_events()
    
    # 리플레이용 새 시스템 생성
    new_sys = SystemController()
    # [중요] 새 시스템에도 'Mgr'가 존재해야 이벤트를 반영할 수 있습니다.
    new_sys.managers["Mgr"] = SimpleNamespace(state="NORMAL", command_queue=[])

    EventReplayer.replay(new_sys, events)
    
    # 이제 'Mgr' 키가 존재하므로 KeyError가 나지 않습니다.
    assert new_sys.managers["Mgr"].state == "IDLE"

def test_replay_with_pause_resume():
    sys = SystemController()
    
    sys.resume() # NORMAL
    sys.pause()  # PAUSED
    sys.resume() # NORMAL
    
    original_state = capture_system_state(sys)
    events = sys.bus.get_events()
    
    new_sys = SystemController()
    EventReplayer.replay(new_sys, events)
    
    assert capture_system_state(new_sys) == original_state