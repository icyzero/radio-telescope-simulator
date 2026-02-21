from src.controller.command import MoveCommand, CMD_SUCCESS, CMD_ABORTED
from src.controller.enums import TelescopeState, CommandType
import pytest

# 1️⃣ 설계하신 FakeTelescope (인터페이스 명칭을 실제 Command 요구사항에 맞춤)
class FakeTelescope:
    def __init__(self):
        self._stopped = False
        self._target_reached = False
        self.move_called = False
        self.state = TelescopeState.IDLE

    def enqueue_move(self, alt, az): # MoveCommand가 호출하는 메서드
        self.move_called = True
        self.state = TelescopeState.MOVING

    def is_target_reached(self):
        return self._target_reached

    def is_stopped(self): # MoveCommand가 중단 여부를 확인할 때 호출
        return self._stopped

    def stop(self):
        self._stopped = True
        self.state = TelescopeState.STOPPED

# 2️⃣ 오늘 달성할 테스트 3개

# ✅ Test 1: execute() 호출 시 망원경에게 이동을 명령하는가?
def test_command_should_delegate_movement_to_telescope_on_execute():
    fake = FakeTelescope()
    cmd = MoveCommand(alt=10, az=10)
    
    cmd.execute(fake)
    
    assert fake.move_called is True
    assert cmd.type == CommandType.MOVE

# ✅ Test 2: 망원경이 목표에 도달하면 Command가 SUCCESS가 되는가?
def test_command_should_transition_to_success_when_telescope_reaches_target():
    fake = FakeTelescope()
    cmd = MoveCommand(alt=10, az=10)
    cmd.execute(fake)
    
    # 망원경이 목표에 도달했다고 가정
    fake._target_reached = True
    
    # 첫 번째 update: has_moved를 True로 만듦
    cmd.update(fake, dt=0.1) 
    # 두 번째 update: has_moved와 target_reached를 모두 만족하여 SUCCESS로 전이
    cmd.update(fake, dt=0.1)
    
    assert cmd.state == CMD_SUCCESS

# ✅ Test 3: 실행 중 망원경이 멈추면 Command가 ABORTED가 되는가?
def test_command_should_transition_to_aborted_when_telescope_is_stopped():
    fake = FakeTelescope()
    cmd = MoveCommand(alt=10, az=10)
    cmd.execute(fake)
    
    # 갑자기 누군가 망원경을 정지시킴
    fake.stop()
    
    # Command 업데이트
    cmd.update(fake, dt=0.1)
    
    assert cmd.state == CMD_ABORTED


"""
1. Command가 Telescope의 내부 좌표를 참조하고 있진 않은가?
A: telescope.alt나 telescope.az 값을 직접 보지 않고 is_target_reached()를 통해 확인하고 있음

2. Command가 Manager를 호출하고 있진 않은가?
A: 하고 있진 않음

3. Command가 시스템 상태를 묻고 있진 않은가?
A: 상태를 묻고 있지 않고 telescope와만 대화하고 있음
-----------------------------------------
Q: 상태 머신인가? 아니면 단순한 행동 트리거인가?
A: 아마도 '상태 머신'
"""