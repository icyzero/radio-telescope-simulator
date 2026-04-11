#src/scheduler/scheduler.py
from src.utils.logger import log
from src.sim.event import Event, EventType, event_pretty_logger
from typing import Optional
from src.sim.bus import EventBus
from src.sim.event_logger import EventLogger
from src.sim.event_metrics import EventMetrics
from src.sim.time_controller import TimeController
from src.sim.telemetry_streamer import TelemetryStreamer

class SystemController:
    def __init__(self):
        self.managers = {}
        self.mode = "NORMAL" #정책만 분기, 흐름 침범X
        self.bus = EventBus()
        self.event_logger = EventLogger()
        self.metrics = EventMetrics() # 분석가 생성
        self.sim_time = 0.0      
        self.time_ctrl = TimeController(scale=1.0)  # [Day 89]]: 시간 제어 엔진 추가
        self._setup_monitoring()
        self.streamer = TelemetryStreamer(self, idle_interval=1.0, active_interval=0.1)
        self.streamer.setup_event_listeners()
        

    def _setup_monitoring(self):
        """중요 이벤트가 터질 때마다 콘솔에 자동으로 출력되도록 설정"""
        #1. 화면 출력용
        monitored_types = [
            EventType.SYSTEM_PAUSED, 
            EventType.SYSTEM_RESUMED,
            EventType.SYSTEM_STOPPED,
            EventType.COMMAND_STARTED,
            EventType.COMMAND_SUCCESS,
            EventType.COMMAND_FAILED,
            EventType.MANAGER_CRITICAL_STOP
        ]
        
        for etype in monitored_types:
            self.bus.subscribe(etype, event_pretty_logger)
        
        # 2. 데이터 기록용 (신규 추가) - 모든 이벤트를 수집
        for etype in EventType:
            self.bus.subscribe(etype, self.event_logger.handle)

        # 분석가가 관심 있는 이벤트들만 구독하게 설정
        relevant_types = [
            EventType.COMMAND_STARTED,
            EventType.COMMAND_SUCCESS,
            EventType.COMMAND_FAILED
        ]
        for etype in relevant_types:
            self.bus.subscribe(etype, self.metrics.handle)

    def register_manager(self, name, manager):
        self.managers[name] = manager
        # 💡 매니저가 시스템의 이벤트를 발행할 수 있도록 주입
        manager.set_event_emitter(self.emit)
        manager.get_system_mode = lambda: self.mode # add_command 호출 시 모드를 전달해야 합니다.
        log(f"[SYSTEM] Manager registered: {name}")

    def pause(self):
        """global_pause의 별칭"""
        self.global_pause()

    def resume(self):
        """global_resume의 별칭"""
        self.global_resume()

    def stop(self):
        """global_stop의 별칭"""
        self.global_stop()

    def is_paused(self) -> bool:
        """현재 시스템이 일시정지 상태인지 확인"""
        return self.mode == "PAUSED"
    
    def set_time_scale(self, scale: float):
        """외부(대시보드 등)에서 배속을 조절할 때 사용"""
        self.time_ctrl.set_scale(scale)
        log(f"[SYSTEM] Time Scale adjusted to x{scale}")

    def update(self, wall_dt):
        # STOPPED 상태면 시스템이 죽은 상태이므로 아무것도 안 함
        if self.mode == "STOPPED":
            return

        # 2. PAUSED 상태면 시간의 흐름(dt)만 차단
        # 하지만 manager.add_command() 등은 update 밖에서 일어나므로 
        # 일시정지 중에도 명령 예약은 가능해집니다.
        if self.mode == "PAUSED":
            return
        
        # [Day 89] 핵심: 현실의 dt를 시뮬레이션 배속이 적용된 dt로 변환
        sim_dt = wall_dt * self.time_ctrl.scale

        self.sim_time += sim_dt # 💡 시뮬레이션 시간 누적 추가
        # 3. NORMAL 상태일 때만 시간을 흐르게 함
        for manager in self.managers.values():
            manager.update(sim_dt) # 매니저와 그 하위 망원경들은 이제 가속된 시간(sim_dt)을 기준으로 움직임

        # [Day 93 추가] 매 프레임마다 스트리머 체크
        self.streamer.tick(self.sim_time)

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

    def get_full_state_snapshot(self):
        return {
            "mode": self.mode,
            "sim_time": self.sim_time,
            "manager_states": {
                name: mgr.get_state() for name, mgr in self.managers.items()
            }
        }
    #Day 83
    def get_full_state(self):
        # SnapshotManager를 이용해 현재 전체 상태를 가져오는 래퍼
        from src.sim.snapshot_manager import SnapshotManager
        # 여기서 last_event_id는 현재 시스템이 마지막으로 처리한 이벤트 ID여야 합니다.
        # 일단 테스트를 위해 임시로 0을 넣거나, 마지막 이벤트를 추적하는 변수를 쓰세요.
        return SnapshotManager.capture(self, last_event_id=getattr(self, 'last_processed_id', 0))
    
    def set_full_state(self, snapshot: dict):
        """스냅샷 데이터를 받아 시스템 상태를 강제 주입(복구)"""
        # 1. 시스템 모드 복구
        self.mode = snapshot.get("system_mode", "NORMAL")
        
        # 2. 마지막 처리 ID 기록 (있다면)
        self.last_processed_id = snapshot.get("last_event_id", 0)
        
        # 3. 각 매니저 상태 복구
        snapshot_managers = snapshot.get("managers", {})
        for name, state in snapshot_managers.items():
            if name in self.managers:
                # 매니저에게 자신의 상태를 스스로 복구하라고 명령
                self.managers[name].set_state(state)

    def get_telemetry(self) -> dict:
        """외부 모니터링을 위한 경량 상태 스냅샷 생성"""
        telemetry = {
            "sim_time": round(self.sim_time, 2),
            "system_mode": self.mode,
            "time_scale": getattr(self.time_ctrl, 'scale', 1.0),
            "managers": {}
        }
        
        for name, mgr in self.managers.items():
            # 매니저로부터 필요한 핵심 물리량만 추출
            tel = mgr.telescope
            telemetry["managers"][name] = {
                "state": mgr.state.__class__.__name__.replace("State", "").upper(),
                "az": round(tel.az, 4),
                "alt": round(tel.alt, 4),
                "target": {"az": tel.target_az, "alt": tel.target_alt},
                "is_moving": tel.state.value == "MOVING"
            }
        return telemetry
    
    def apply_config(self, params: dict):
        """실시간 설정 반영 및 이벤트 발행"""
        for key, value in params.items():
            if key == "slew_rate":
                # 모든 망원경 매니저에 속도 설정 반영
                for mgr in self.managers.values():
                    mgr.telescope.slew_rate = value # mgr.telescope가 slew_rate 속성을 가지고 있는지 확인
            
            # 🚨 변경 이력 기록 (Audit Log)
            self.emit(
                EventType.CONFIG_CHANGED, 
                "SystemController", 
                {"parameter": key, "new_value": value}
            )
        return True
    
    def get_diagnostics(self):
        """시스템의 전체적인 건강 상태 리포트 생성 (안전 강화 버전)"""
        # Metrics 안전하게 가져오기
        metrics = getattr(self, 'metrics', None)
        total = getattr(metrics, 'total_commands', 0) if metrics else 0
        failed = getattr(metrics, 'failed_count', 0) if metrics else 0
        success_rate = ((total - failed) / total * 100) if total > 0 else 100.0

        report = {
            "system": {
                "mode": getattr(self, 'mode', 'UNKNOWN'),
                "sim_time": round(getattr(self, 'sim_time', 0.0), 2),
                "managers_count": len(self.managers)
            },
            "performance": {
                "total_commands": total,
                "failed_count": failed,
                "success_rate": f"{round(success_rate, 1)}%"
            },
            "hardware_configs": {}
        }

        for name, mgr in self.managers.items():
            tel = mgr.telescope
            # state가 Enum인지 확인하고 안전하게 이름 가져오기
            state_display = tel.state.name if hasattr(tel.state, 'name') else str(tel.state)
            
            report["hardware_configs"][name] = {
                "slew_rate": getattr(tel, 'slew_rate', 'N/A'),
                "current_pos": {
                    "az": round(getattr(tel, 'az', 0.0), 3),
                    "alt": round(getattr(tel, 'alt', 0.0), 3)
                },
                "state": state_display
            }
        
        return report