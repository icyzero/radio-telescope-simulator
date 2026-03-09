# tests/unit/test_command_lifecycle.py
import pytest
from src.sim.event import EventType
from src.controller.command import MoveCommand
from src.controller.command import Command, CommandType

class FailingCommand(Command):
    def __init__(self):
        super().__init__()
        self.type = CommandType.MOVE
        self.state = None # 초기 상태

    def execute(self, telescope=None, prefix=""):
        # 실행되는 즉시 예외 발생
        raise RuntimeError("하드웨어 통신 오류 시뮬레이션")

    def update(self, telescope, dt, prefix=""):
        pass

def test_full_command_lifecycle_events(system):
    """명령이 시작부터 성공까지 모든 이벤트를 올바르게 발행하는지 확인"""
    
    manager_a = system.managers.get("A")
    manager_a.add_command(MoveCommand(alt=10, az=10))
    
    # 최대 10초까지 1초씩 업데이트하며 SUCCESS가 뜰 때까지 대기
    for _ in range(10):
        # 2. 시스템 업데이트 (시간을 흘려보냄)
        system.update(1.0)
        history = system.bus.get_history()
        event_types = [e.type for e in history]
        # 3. 히스토리 검증
        if EventType.COMMAND_SUCCESS in event_types:
            break

    assert EventType.COMMAND_STARTED in event_types
    assert EventType.COMMAND_SUCCESS in event_types

def test_command_failure_lifecycle_event(system):
    """명령 실패 시 FAILED 이벤트가 발행되는지 확인"""
    manager_a = system.managers.get("A")
    
    # 1. 무조건 실패하는 명령 투입
    manager_a.add_command(FailingCommand())
    
    # 2. 시스템 업데이트 (실행 시도)
    system.update(1.0)
    
    # 3. 히스토리 검증
    history = system.bus.get_history()
    event_types = [e.type for e in history]
    
    # STARTED는 찍혔을 것이고, 결과는 SUCCESS가 아닌 FAILED여야 함
    assert EventType.COMMAND_STARTED in event_types
    assert EventType.COMMAND_FAILED in event_types
    assert EventType.COMMAND_SUCCESS not in event_types

    # 4. 페이로드 검증 (에러 메시지가 잘 담겼는지 확인)
    failed_event = system.bus.get_history(EventType.COMMAND_FAILED)[0]
    
    # 방법 A: 실제 에러 메시지 내용으로 검사 (추천)
    assert "하드웨어 통신 오류 시뮬레이션" in failed_event.payload.get("error")
    
    # 또는 방법 B: 어떤 에러든 메시지가 들어있는지만 검사
    assert len(failed_event.payload.get("error")) > 0