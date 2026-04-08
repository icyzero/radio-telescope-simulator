# tests/integration/test_adaptive_streaming.py

import pytest
from src.scheduler.scheduler import SystemController
from src.controller.telescope import Telescope, TelescopeState
from src.controller.command_manager import CommandManager
from src.sim.event import EventType

def test_adaptive_streaming_logic():
    ctrl = SystemController()
    tel = Telescope()
    mgr = CommandManager("Main", tel)
    ctrl.register_manager("Main", mgr)
    
    # 스트리머 이벤트 리스너 활성화
    ctrl.streamer.setup_event_listeners()

    # 1. 초기 상태 (IDLE): 1.0초 동안 1.0s 주기로 패킷 발생 확인
    for _ in range(10): # 0.1s * 10 = 1.0s
        ctrl.update(0.1)
    
    # 시작 시점 포함 약 1~2개 예상
    idle_packet_count = len(ctrl.streamer.stream_buffer)
    
    # 2. 이동 명령 주입 (ACTIVE 모드 진입)
    tel.state = TelescopeState.MOVING # 강제 상태 변경 또는 명령 주입
    
    # 1.0초 동안 0.1s 주기로 패킷 발생 확인
    for _ in range(12): # 0.1s * 12 = 1.2s
        ctrl.update(0.1)
    
    active_packet_count = len(ctrl.streamer.stream_buffer) - idle_packet_count
    
    # ACTIVE 모드일 때 패킷이 훨씬 많아야 함 (약 10개)
    assert active_packet_count > idle_packet_count
    print(f"\n[ADAPTIVE TEST] Idle Packets: {idle_packet_count}, Active Packets: {active_packet_count}")

    # 3. 즉시 푸시 테스트
    initial_count = len(ctrl.streamer.stream_buffer)
    ctrl.emit(EventType.COMMAND_FAILED, "TestUnit") # 에러 강제 발생
    
    assert len(ctrl.streamer.stream_buffer) == initial_count + 1
    assert ctrl.streamer.stream_buffer[-1]["stream_reason"] == "EVENT_COMMAND_FAILED"