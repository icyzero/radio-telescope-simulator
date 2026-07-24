# tests/integration/test_streaming.py

import pytest
from src.scheduler.scheduler import SystemController
from src.controller.telescope import Telescope
from src.controller.command_manager import CommandManager
from src.controller.command import MoveCommand


def test_telemetry_streaming_frequency():
    ctrl = SystemController()
    # 매니저를 등록하고 실제로 망원경을 움직여야 스트리머가 ACTIVE(0.1초) 모드로 전환됨
    tel = Telescope(slew_rate=5.0)
    mgr = CommandManager("A", tel)
    ctrl.register_manager("A", mgr)
    mgr.add_command(MoveCommand(alt=30, az=90))

    # 시뮬레이션 시간을 1.0초 동안 흘림 (0.05초씩 20번 업데이트)
    for _ in range(20):
        ctrl.update(0.05)
    
    # 시뮬레이션 시간을 1.0초 동안 흘림 (0.05초씩 20번 업데이트)
    for _ in range(20):
        ctrl.update(0.05)
    
    buffer = ctrl.streamer.stream_buffer
    
    # 확인 1: 1.0초 동안 0.1초 간격이면 총 10개(+알파)의 패킷이 쌓여야 함
    # (시작 시점 포함 여부에 따라 10~11개)
    assert len(buffer) >= 10, f"패킷 개수 부족: {len(buffer)}"
    
    # 확인 2: 첫 번째 패킷과 두 번째 패킷의 sim_time 차이가 0.1초인지 확인
    t1 = buffer[0]['sim_time']
    t2 = buffer[1]['sim_time']
    assert round(t2 - t1, 1) == 0.1
    
    print(f"\n[STREAM TEST] Total Packets: {len(buffer)}")
    print(f"[STREAM TEST] Last Packet Time: {buffer[-1]['sim_time']}s")