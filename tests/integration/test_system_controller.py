import pytest
from src.scheduler.scheduler import SystemController
from src.controller.command_manager import CommandManager
from src.controller.telescope import Telescope
from src.controller.command import MoveCommand, CMD_ABORTED
from src.controller.enums import TelescopeState

# ✅ 시나리오 1: 다중 실행 및 전역 정지
def test_system_should_propagate_stop_to_all_registered_managers_on_global_stop(system):
    """
    Given: 시스템에 두 개의 매니저(A, B)가 등록되어 실행 중일 때
    When: 전역 정지(global_stop)를 호출하면
    Then: 모든 매니저와 망원경이 즉시 정지되어야 한다.
    """
    # 1. 추가 매니저 구성 (이미 fixture에서 A는 등록되어 있을 수 있으므로 B 위주로 추가)
    # fixture의 system을 활용하되, 독립적인 테스트를 위해 추가 등록
    
    tele_b = Telescope()
    manager_b = CommandManager("B", tele_b)
    system.register_manager("B", manager_b)

    # fixture에서 온 A 매니저 가져오기
    manager_a = system.managers["A"]
    tele_a = manager_a.telescope
    
    # 2. 명령 하달 (분권형)
    manager_a.add_command(MoveCommand(alt=10, az=10))
    manager_b.add_command(MoveCommand(alt=20, az=20))
    
    # 3. 가동 시작
    system.update(0.1)
    assert tele_a.state == TelescopeState.MOVING
    assert tele_b.state == TelescopeState.MOVING
    
    # 4. 전역 정지 (이 때 SystemController 내부에서 모든 manager.stop()을 호출해야 함)
    system.global_stop()
    
    # 5. 검증: 모든 계층이 멈췄는가?
    assert tele_a.state == TelescopeState.STOPPED
    assert tele_b.state == TelescopeState.STOPPED
    assert manager_a.current is None
    assert manager_b.current is None

# ✅ 시나리오 2: STOP 우선 정책 검증
def test_global_stop_should_override_command_success_policy_in_the_same_tick(system):
    """
    Given: 아주 짧은 거리의 명령이 실행되어 성공 직전인 상태에서
    When: 같은 틱에 global_stop이 발생하면
    Then: SUCCESS가 아닌 ABORTED로 종료되어야 한다 (안전 우선 정책).
    """
    manager = system.managers["A"]
    tele = manager.telescope
    
    # 아주 짧은 거리 이동 (한 틱에 성공 가능한 거리)
    cmd = MoveCommand(alt=0.001, az=0.001)
    manager.add_command(cmd)
    
    # 업데이트와 동시에 중단 호출
    # 만약 SUCCESS가 우선이라면 cmd.state는 SUCCESS가 됨
    # 만약 STOP이 우선이라면 cmd.state는 ABORTED가 됨
    system.update(0.1)
    system.global_stop()
    
    # 운영 철학 확인
    assert cmd.state == CMD_ABORTED
    assert tele.state == TelescopeState.STOPPED


"""
02.20
Q1: Global STOP은 명령인가? 정책 이벤트인가?
A: 정책 이벤트
    만약 명령이었다면 큐에서 자기 차례를 기다려야 하지만 stop이 들어오는 순간 모든 큐를 파괴시켰기 때문

Q2: Scheduler는 단순 전달자인가? 정책 필터인가?
A: 정책 필터
    명령을 전달해도 되는 평시인지 모든 명령을 차단/정지시켜야 하는 비상시인지 결정하는 최상위 필터
"""

"""
02.21
Q: 지금 테스트들은: “행복 경로” 중심인가? 아니면 “실패 경로”도 충분한가?
A: 행복 경로: 명령을 주면 잘 가고, 도착하면 성공하고, 다음 명령을 꺼냄
    긴급 경로 (STOP): 비상시엔 모든 것을 파괴하고 멈춤
"""