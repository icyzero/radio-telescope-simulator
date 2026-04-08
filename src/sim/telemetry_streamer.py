# src/sim/telemetry_streamer.py

from src.sim.event import EventType
from src.controller.enums import TelescopeState

class TelemetryStreamer:
    def __init__(self, controller, idle_interval=1.0, active_interval=0.1):
        self.controller = controller
        self.idle_interval = idle_interval
        self.active_interval = active_interval
        self.current_interval = idle_interval # 기본은 Idle 모드
        
        self.last_stream_time = -self.current_interval
        self.stream_buffer = []

    def _determine_interval(self):
        """시스템 상태에 따라 주기를 결정"""
        # 하나라도 MOVING 상태인 매니저가 있는지 확인
        is_active = any(
            mgr.telescope.state == TelescopeState.MOVING 
            for mgr in self.controller.managers.values()
        )
        return self.active_interval if is_active else self.idle_interval

    def tick(self, sim_time):
        # 1. 이전 주기 저장
        old_interval = self.current_interval
        
        # 2. 새로운 주기 결정
        self.current_interval = self._determine_interval()

        # 3. 💡 [핵심] 모드 전환 감지 (Idle -> Active)
        # 주기가 작아졌다면(더 빨라졌다면) 기다리지 않고 즉시 푸시!
        if self.current_interval < old_interval:
            print(f"[STREAMER] Mode changed to ACTIVE. Immediate push at {sim_time}")
            self.push_telemetry(sim_time, reason="MODE_CHANGED")
            return # 이번 틱은 여기서 종료

        # 4. 일반적인 주기적 전송 체크
        if sim_time >= self.last_stream_time + self.current_interval:
            self.push_telemetry(sim_time)

    def push_telemetry(self, sim_time, reason="PERIODIC"):
        """실제 패킷을 생성하여 버퍼에 넣음"""
        packet = self.controller.get_telemetry()
        packet["stream_reason"] = reason # 왜 보내졌는지 기록 (분석용)
        self._send(packet) 
        self.last_stream_time = sim_time    

    def _send(self, packet):
        """실제 소켓 전송 전, 버퍼에 쌓는 로직"""
        # 실제 환경에서는 여기서 socket.send()나 MQTT publish가 일어납니다.
        self.stream_buffer.append(packet)

    def clear_buffer(self):
        self.stream_buffer.clear()

    def setup_event_listeners(self):
        """중요 이벤트 발생 시 즉시 전송하도록 리스너 등록"""
        critical_events = [
            EventType.COMMAND_FAILED,
            EventType.MANAGER_CRITICAL_STOP,
            EventType.SYSTEM_STOPPED
        ]
        for etype in critical_events:
            self.controller.bus.subscribe(etype, self.on_critical_event)

    def on_critical_event(self, event):
        """이벤트 수신 즉시 패킷 생성 (Interval 무시)"""
        print(f"[STREAMER] Critical Event Detected: {event.type}. Pushing immediate telemetry.")
        self.push_telemetry(self.controller.sim_time, reason=f"EVENT_{event.type.name}")