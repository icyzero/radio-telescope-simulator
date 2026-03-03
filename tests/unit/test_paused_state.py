# tests/unit/test_paused_state.py
import pytest
from src.controller.state import PausedState
from src.controller.command import MoveCommand

def test_paused_state_queues_commands(manager):  # 👈 mock_manager에서 manager로 변경
    # Given: PausedState인 상황
    state = PausedState()
    cmd = MoveCommand(alt=10, az=10)
    
    # When: Paused 상태에서 명령 추가 시도
    # (manager 객체는 이미 conftest.py 등을 통해 주입된 실제 혹은 Mock 객체일 것입니다)
    state.handle_add_command(manager, cmd, "PAUSED")
    
    # Then: 즉시 실행(current)되지 않고 큐(queue)에만 들어가야 함
    assert manager.current is None
    assert cmd in manager.queue
    assert len(manager.queue) == 1