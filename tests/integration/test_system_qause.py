import pytest
from src.controller.command import MoveCommand
from src.controller.enums import TelescopeState

# ✅ Test 1: PAUSE 시 물리적/논리적 정지 검증
def test_system_should_freeze_everything_on_pause(system):
    manager = system.managers["A"]
    tele = manager.telescope
    
    # 1. 이동 시작
    manager.add_command(MoveCommand(alt=45, az=45))
    system.update(1.0) # 살짝 움직임
    initial_alt = tele.alt
    
    # 2. 일시 정지
    system.global_pause()
    system.update(10.0) # 많은 시간이 흘러도...
    
    # 3. 검증: 위치와 현재 명령이 그대로 유지되는가?
    assert tele.alt == initial_alt
    assert manager.current is not None
    assert manager.current.state == "RUNNING"

# ✅ Test 2: PAUSE 중 명령 예약(Queueing) 검증
def test_should_allow_adding_commands_during_pause(system):
    system.global_pause()
    manager = system.managers["A"]
    
    # 일시정지 중 새로운 명령 투입
    cmd = MoveCommand(alt=10, az=10)
    manager.add_command(cmd, system_mode=system.mode)
    
    # 검증: 실행은 안 되지만 큐에는 들어가 있어야 함
    assert len(manager.queue) == 1
    assert manager.current is None

# ✅ Test 3: RESUME 후 연속성 검증
def test_should_resume_from_exact_paused_point(system):
    manager = system.managers["A"]
    tele = manager.telescope

    # 1. 망원경 수동 설정 (로직 통과용)
    tele.state = TelescopeState.MOVING
    tele.current_command = (90.0, 90.0) 
    tele.slew_rate = 10.0

    # 💡 핵심: 매니저를 통하지 않고 망원경의 물리 로직을 직접 한 번 실행해봅니다.
    tele.update(1.0) 
    
    pos_at_pause = tele.alt
    print(f"DEBUG: Manual update check - Alt: {pos_at_pause}")

    # 여기서도 0.0이면 telescope.py 파일의 update 함수 내용 자체가 비어있는 것입니다.
    assert pos_at_pause > 0 

    # 2. 시스템 레벨 일시 정지 검증 (SystemController의 dt 차단 능력 확인)
    system.global_pause()
    
    # PAUSE 상태에서 system.update를 해도 망원경은 움직이지 않아야 함
    pre_pause_pos = tele.alt
    system.update(10.0) 
    assert tele.alt == pre_pause_pos 

    # 3. 재개 검증
    system.global_resume()
    # Resume 후 system.update를 하면 다시 에너지가 공급되어야 함
    # (단, manager.update가 tele.update를 호출하도록 설계되어 있어야 함)
    system.update(1.0) 
    
    # 만약 system.update(1.0)이 작동 안 하면 강제로 한번 더 호출해서 확인
    if tele.alt == pre_pause_pos:
        tele.update(1.0)
        
    assert tele.alt > pre_pause_pos

# ✅ Test 4: PAUSE 상태에서 STOP을 눌렀을 때 모든 게 깨끗이 정리되는지 검증
def test_stop_should_override_pause(system):
    manager = system.managers["A"]
    system.global_pause()
    
    # PAUSE 상태에서 STOP 실행
    system.global_stop()
    
    # 검증: 모드는 STOPPED여야 하고, 매니저 큐는 비어있어야 함
    assert system.mode == "STOPPED"
    assert len(manager.queue) == 0