from src.utils.logger import log
from src.controller.enums import CommandType, TelescopeState

CMD_PENDING = "PENDING"
CMD_RUNNING = "RUNNING"
CMD_SUCCESS = "SUCCESS"
CMD_FAILED = "FAILED" #조건 불충족 시 실패
CMD_ABORTED = "ABORTED" #외부 요인 시 중단


class Command: #명령에 '시간'을 붙일 수 있는 구조 
    def __init__(self, scheduled_at=0.0, priority=1): #priority 상태 stop = 0 / move = 1 / park = 2 
        self.state = CMD_PENDING
        self.scheduled_at = scheduled_at
        self.priority = priority 
        self.type = None

    def execute(self, telescope, prefix=None): #명령 발동 트리거 (target 설정, 상태 running)
        self.state = CMD_RUNNING
        raise NotImplementedError
    
    def update(self, telescope, dt, prefix=None): #명령 결과 관찰기 telescope의 상태를 보고 성공/실패 판단 | dt = 시간 기반 실패 판단
        pass

    def abort(self, prefix=None):
        self.state = CMD_ABORTED
    
class MoveCommand(Command):
    def __init__(self, alt, az, scheduled_at=0.0, timeout=30.0):
        super().__init__(scheduled_at)
        self.alt = alt
        self.az = az
        self.elapsed_time = 0.0
        self.timeout = timeout
        self.abort_reason = None # 외부요인 중단
        self.fail_reason = None  # 조건 불충족 조건
        self.type = CommandType.MOVE
        self.has_moved = False

    def execute(self, telescope, prefix=None):
        log("[CMD] MoveCommand START", prefix=prefix)
        self.state = CMD_RUNNING
        log("[CMD] MoveCommand RUNNING", prefix=prefix)
        telescope.enqueue_move(self.alt, self.az)

    def abort(self, prefix=None, reason="INTERRUPTED"):
        self.abort_reason = reason
        self.state = CMD_ABORTED
        log("[CMD] MoveCommand ABORTED ({reason}))", prefix=prefix)

    def update(self, telescope, dt, prefix=None):
        if self.state != CMD_RUNNING:
            return
        
        self.elapsed_time += dt #시간 누적

        if telescope.is_stopped(): # 외부요인 중단
            self.state = CMD_ABORTED
            self.abort_reason = "TELESCOPE_STOPPED"
            log("[CMD] MoveCommand ABORTED (TELESCOPE_STOPPED)", prefix=prefix)
            return

        if self.has_moved and telescope.is_target_reached(): #성공 조건
            self.state = CMD_SUCCESS 
            log("[CMD] MoveCommand SUCCESS", prefix=prefix)
            return
        
        if self.elapsed_time > self.timeout: # 조건 불충족 조건
            self.state = CMD_FAILED
            self.fail_reason = "TIMEOUT"
            log("[CMD] MoveCommand FAILED (TIMEOUT)", prefix=prefix)
            return
        
        if telescope.state == TelescopeState.MOVING:
            self.has_moved = True

class StopCommand(Command):
    def __init__(self, scheduled_at=0):
        super().__init__(scheduled_at)
        self.type = CommandType.STOP

    def execute(self, telescope, prefix=None):
        log("[CMD] StopCommand START", prefix=prefix)
        telescope.stop()
        self.state = CMD_SUCCESS
        log("[CMD] StopCommand SUCCESS",prefix=prefix)