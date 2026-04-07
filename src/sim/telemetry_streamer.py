# src/sim/telemetry_streamer.py

class TelemetryStreamer:
    def __init__(self, controller, interval=0.1):
        self.controller = controller
        self.interval = interval
        self.last_stream_time = -interval
        self.stream_buffer = []  # 가상 네트워크 버퍼 (Mock)
        self.last_sent_hash = None # Delta 전송을 위한 이전 상태 기록

    def tick(self, sim_time):
        """SystemController.update()에서 호출됨"""
        # 1. 고정 주기(Interval) 체크
        if sim_time >= self.last_stream_time + self.interval:
            packet = self.controller.get_telemetry()
            
            # 2. [선택 사항] 데이터 차분(Delta) 판단 로직
            # 여기서는 간단히 전체 패킷의 해시나 값을 비교할 수 있습니다.
            # 지금은 우선 모든 패킷을 스트리밍하는 'Heartbeat' 모드로 구현합니다.
            
            self._send(packet)
            self.last_stream_time = sim_time

    def _send(self, packet):
        """실제 소켓 전송 전, 버퍼에 쌓는 로직"""
        # 실제 환경에서는 여기서 socket.send()나 MQTT publish가 일어납니다.
        self.stream_buffer.append(packet)

    def clear_buffer(self):
        self.stream_buffer.clear()