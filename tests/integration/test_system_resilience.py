import pytest
from src.controller.command import MoveCommand, CMD_FAILED
from src.controller.enums import TelescopeState

# ✅ 1 & 5 통합: STOP 상태에서의 명령 차단 테스트
def test_should_reject_new_commands_when_system_is_in_stopped_state(system):
    # 1. 시스템을 정지 상태로 만듦
    system.global_stop()
    manager = system.managers["A"]
    
    # 2. 새로운 명령 투입 시도
    cmd = MoveCommand(alt=10, az=10)
    manager.add_command(cmd)
    
    # 3. 검증: 명령이 무시되고 큐가 비어있어야 함
    assert manager.current is None
    assert len(manager.queue) == 0

# ✅ 2: 명령 실패 시 후속 명령 중단 테스트
def test_should_halt_execution_and_clear_queue_when_command_fails(manager):
    cmd1 = MoveCommand(alt=10, az=10)
    cmd2 = MoveCommand(alt=20, az=20)
    
    manager.add_command(cmd1)
    manager.add_command(cmd2)
    
    # 강제로 첫 번째 명령을 FAILED로 만듦
    cmd1.state = "FAILED"
    manager.update(0.1)
    
    # 검증: 두 번째 명령이 실행되지 않고 큐가 정리되었는가? (정책에 따라 다름)
    # 여기서는 안전을 위해 큐를 비우는 정책을 테스트
    assert manager.current is None
    assert len(manager.queue) == 0

# ✅ 3: dt = 0 경계 조건 테스트
def test_system_should_not_change_state_when_dt_is_zero(system):
    manager = system.managers["A"]
    tele = manager.telescope
    
    initial_alt = tele.alt
    manager.add_command(MoveCommand(alt=45, az=45))
    
    # 시간이 흐르지 않음
    system.update(0)
    
    assert tele.alt == initial_alt
    assert tele.state == TelescopeState.MOVING # 상태는 변할 수 있으나 위치는 그대로

# ✅ 4: 매우 큰 dt에 대한 물리 안정성 테스트
def test_telescope_should_not_overshoot_massively_on_huge_dt(telescope):
    telescope.enqueue_move(alt=10, az=10)
    
    # 비정상적으로 큰 시간 주입
    telescope.update(100000.0)
    
    # 검증: 목표치에 딱 멈춰있거나, 에러를 내야 함 (순간이동 방지)
    assert abs(telescope.alt - 10) < 0.1 
    assert telescope.v_alt == 0


"""
Q: 이 시스템은: FAIL-SAFE인가? 아니면 FAIL-SILENT인가?
A: FAIL-SAFE 설계
    실패 발생 시 IDLE/STOPPED로 전이하고 피해 최소화
"""