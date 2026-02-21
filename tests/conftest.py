# tests/conftest.py (모든 테스트에서 공통으로 쓸 Fixture 저장소)
import pytest
from src.controller.telescope import Telescope
from src.controller.command_manager import CommandManager

@pytest.fixture
def telescope():
    """깨끗한 상태의 망원경 객체 제공"""
    return Telescope()

@pytest.fixture
def manager(telescope):
    """망원경과 연결된 기본 매니저 제공"""
    return CommandManager("A", telescope)

@pytest.fixture
def system(manager):
    """매니저가 등록된 시스템 컨트롤러 제공"""
    from src.scheduler.scheduler import SystemController
    ctrl = SystemController()
    ctrl.register_manager("A", manager)
    return ctrl