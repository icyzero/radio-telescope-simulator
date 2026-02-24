#src/scheduler/scheduler.py
from src.utils.logger import log

class SystemController:
    def __init__(self):
        self.managers = {}
        self.mode = "NORMAL" #정책만 분기, 흐름 침범X

    def register_manager(self, name, manager):
        self.managers[name] = manager
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

        # 3. NORMAL 상태일 때만 시간을 흐르게 함
        for manager in self.managers.values():
            manager.update(dt)

    def global_stop(self):
        self.mode = "STOPPED"  # 모드 변경
        log("[SYSTEM] GLOBAL STOP triggered.")
        
        # 💡 일시정지 중이더라도 하드웨어 정지 명령은 즉시 전파되어야 함
        for manager in self.managers.values():
            manager.stop() # 각 매니저의 큐를 비우고 망원경을 STOPPED 상태로 만듦

    def global_pause(self):
        if self.mode == "NORMAL":
            self.mode = "PAUSED"
            log("[SYSTEM] GLOBAL PAUSE triggered. State preserved.")

    def global_resume(self):
        if self.mode == "PAUSED":
            self.mode = "NORMAL"
            log("[SYSTEM] GLOBAL RESUME. Continuing operations.")