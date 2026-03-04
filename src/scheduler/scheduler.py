#src/scheduler/scheduler.py
from src.utils.logger import log
from src.sim.event import Event, EventBus, EventType
from typing import Optional
from src.sim.bus import EventBus

class SystemController:
    def __init__(self):
        self.managers = {}
        self.mode = "NORMAL" #정책만 분기, 흐름 침범X
        self.bus = EventBus()
        self.sim_time = 0.0        

    def register_manager(self, name, manager):
        self.managers[name] = manager
        # 💡 매니저가 시스템의 이벤트를 발행할 수 있도록 주입
        manager.set_event_emitter(self.emit)
        manager.get_system_mode = lambda: self.mode # add_command 호출 시 모드를 전달해야 합니다.
        log(f"[SYSTEM] Manager registered: {name}")

    def update(self, dt):
        # STOPPED 상태면 시스템이 죽은 상태이므로 아무것도 안 함
        if self.mode == "STOPPED":
            return

        # 2. PAUSED 상태면 시간의 흐름(dt)만 차단
        # 하지만 manager.add_command() 등은 update 밖에서 일어나므로 
        # 일시정지 중에도 명령 예약은 가능해집니다.
        if self.mode == "PAUSED":
            return

        self.sim_time += dt # 💡 시뮬레이션 시간 누적 추가
        # 3. NORMAL 상태일 때만 시간을 흐르게 함
        for manager in self.managers.values():
            manager.update(dt)

    def global_stop(self):
        self.mode = "STOPPED"  # 모드 변경
        self.emit(EventType.SYSTEM_STOPPED, "SystemController") # 💡 이벤트 발행
        #log("[SYSTEM] GLOBAL STOP triggered.")
        
        # 💡 일시정지 중이더라도 하드웨어 정지 명령은 즉시 전파되어야 함
        for manager in self.managers.values():
            manager.stop() # 각 매니저의 큐를 비우고 망원경을 STOPPED 상태로 만듦

    def global_pause(self):
        if self.mode == "NORMAL":
            self.mode = "PAUSED"
            self.emit(EventType.SYSTEM_PAUSED, "SystemController") # 💡 이벤트 발행
            #log("[SYSTEM] GLOBAL PAUSE triggered. State preserved.")

    def global_resume(self):
        if self.mode == "PAUSED":
            self.mode = "NORMAL"
            self.emit(EventType.SYSTEM_RESUMED, "SystemController") # 💡 이벤트 발행
            #log("[SYSTEM] GLOBAL RESUME. Continuing operations.")

    def emit(self, event_type: EventType, source: str, payload: Optional[dict] = None):
        """모든 계층의 이벤트를 수집하는 중앙 창구"""
        event = Event(
            type=event_type,
            source=source,
            payload=payload or {},
            sim_time=self.sim_time
        )
        self.bus.publish(event)
        # 로그에도 남겨서 실시간 모니터링 가능하게 함
        log(f" {event_type} | Source: {source} | SimTime: {self.sim_time:.2f}s")