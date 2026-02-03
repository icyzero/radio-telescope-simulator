from src.utils.logger import log

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

    def execute(self, telescope): #명령 발동 트리거 (target 설정, 상태 running)
        self.state = CMD_RUNNING
        raise NotImplementedError
    
    def update(self, telescope, dt): #명령 결과 관찰기 telescope의 상태를 보고 성공/실패 판단 | dt = 시간 기반 실패 판단
        pass
    
class MoveCommand(Command):
    def __init__(self, alt, az, scheduled_at=0.0):
        super().__init__(scheduled_at)
        self.alt = alt
        self.az = az
        self.elapsed_time = 0.0
        self.timeout = 30.0 #seconds
        self.fail_reason = None

    def execute(self, telescope):
        log("[CMD] MoveCommand START")
        self.state = CMD_RUNNING
        log("[CMD] MoveCommand RUNNING")
        telescope.enqueue_move(self.alt, self.az)

    def update(self, telescope, dt):
        if self.state != CMD_RUNNING:
            return
        
        self.elapsed_time += dt #시간 누적

        if telescope.is_stopped():
            self.state = CMD_ABORTED
            self.abort_reason = "TELESCOPE_STOPPED"
            log("[CMD] MoveCommand ABORTED (TELESCOPE_STOPPED)")
            return

        if telescope.state == "IDLE" and telescope.is_target_reached(): #성공 조건
            self.state = CMD_SUCCESS 
            log("[CMD] MoveCommand SUCCESS")
            return
        
        if self.elapsed_time > self.timeout: #실패 조건
            self.state = CMD_FAILED
            self.fail_reason = "TIMEOUT"
            log("[CMD] MoveCommand FAILED (TIMEOUT)")
            return

class StopCommand(Command):
    def __init__(self, scheduled_at=0):
        super().__init__(scheduled_at)

    def execute(self, telescope):
        print("[CMD] StopCommand START")
        telescope.stop()
        self.state = CMD_SUCCESS
        print("[CMD] StopCommand SUCCESS")