from src.controller.command_manager import CommandManager
from src.controller.enums import TelescopeState, CommandType
import pytest

class FakeCommand:
    def __init__(self, cmd_type, priority=0, scheduled_at=0.0):
        self.type = cmd_type
        self.priority = priority        # 💡 추가: Manager가 정렬할 때 사용
        self.scheduled_at = scheduled_at # 💡 추가: Manager가 실행 시점 판단할 때 사용
        self.state = "READY"
        self.executed = False
        self.aborted = False

    def execute(self, telescope, prefix=None):
        self.executed = True
        self.state = "RUNNING"
        telescope.state = TelescopeState.MOVING # 상태 연동

    def abort(self, prefix=None):
        self.aborted = True
        self.state = "ABORTED"

    def update(self, telescope, dt, prefix=None):
        pass

# FakeTelescope (Manager 초기화에 필요)
class FakeTelescope:
    def __init__(self):
        self.state = TelescopeState.IDLE
        self._stopped = False

    def update(self, dt): pass

    def stop(self): 
        self.state = TelescopeState.STOPPED
        self._stopped = True

    def is_stopped(self): return self._stopped

# ✅ Test 1: IDLE 상태에서 MOVE 수락 후 즉시 실행
def test_manager_accept_and_execute():
    telescope = FakeTelescope()
    manager = CommandManager("A", telescope)
    cmd = FakeCommand(CommandType.MOVE)

    manager.add_command(cmd)

    assert manager.current == cmd
    assert cmd.executed is True
    assert cmd.state == "RUNNING"

# ✅ Test 2: RUNNING 중 새 MOVE는 PENDING 되는가?
def test_manager_queueing():
    manager = CommandManager("A", FakeTelescope())
    cmd1 = FakeCommand(CommandType.MOVE)
    cmd2 = FakeCommand(CommandType.MOVE)

    manager.add_command(cmd1) # cmd1 실행 시작
    manager.add_command(cmd2) # cmd2는 큐로

    assert manager.current == cmd1
    assert len(manager.queue) == 1
    assert manager.queue[0] == cmd2
    assert cmd2.executed is False # 아직 실행 전이어야 함

# ✅ Test 3: RUNNING Command SUCCESS 시 다음 명령 실행
def test_manager_sequencing():
    manager = CommandManager("A", FakeTelescope())
    cmd1 = FakeCommand(CommandType.MOVE)
    cmd2 = FakeCommand(CommandType.MOVE)

    manager.add_command(cmd1)
    manager.add_command(cmd2)

    # 강제로 cmd1을 성공 상태로 변경
    cmd1.state = "SUCCESS" 
    
    # Manager 업데이트 -> 큐 확인 루프 작동
    # 첫 번째 update: cmd1의 종료를 감지하고 current를 None으로 만듦
    manager.update(0.1) 
    
    # 두 번째 update: current가 None인 것을 보고 큐에서 cmd2를 꺼내 실행함
    manager.update(0.1)

    assert manager.current == cmd2
    assert cmd2.executed is True
    assert len(manager.queue) == 0

# ✅ Test 4: STOP 개입 시 queue clear + 현재 흐름 중단
def test_manager_stop_behavior():
    manager = CommandManager("A", FakeTelescope())
    cmd1 = FakeCommand(CommandType.MOVE)
    manager.add_command(cmd1)
    manager.add_command(FakeCommand(CommandType.MOVE)) # 큐에 하나 추가

    manager.stop()

    assert len(manager.queue) == 0
    assert manager.current is None
    assert manager.telescope.state == TelescopeState.STOPPED

"""
1. Manager가 Command 내부 상태에 과도하게 의존하는가?
A: STATE_COMMAND_RULES 규칙 테이블에 근거하여 결정함

2. Manager가 Telescope 상태를 직접 참조하는가?
A: state, scheduled_at만 확인
    내용이 아닌 생명 주기만 관리

3. STOP이 Command처럼 동작하는가, 아니면 개입 이벤트인가?
A: 개입 이벤트
    큐에 쌓이지 않고 즉시 정지 시킴
---
Q. CommandManager는 상태 머신인가? 아니면 흐름 오케스트레이터인가?
A: 오케스트레이터
    Manager가 스스로 전이가 아닌 하부 객체들의 상태를 모니터링하고 순서를 조율하기 때문
"""