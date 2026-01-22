CMD_PENDING = "PENDING"
CMD_RUNNING = "RUNNING"
CMD_SUCCESS = "SUCCESS"
CMD_FAILED = "FAILED" #조건 불충족 시 실패
CMD_ABORTED = "ABORTED" #외부 요인 시 중단


class Command: #명령에 '시간'을 붙일 수 있는 구조 
    def __init__(self):
        self.state = CMD_PENDING

    def execute(self, telescope): #명령 발동 트리거 (target 설정, 상태 running)
        self.state = CMD_RUNNING
        raise NotImplementedError
    
    def update(self, telescope, dt): #명령 결과 관찰기 telescope의 상태를 보고 성공/실패 판단 | dt = 시간 기반 실패 판단
        pass
    
class MoveCommand(Command):
    def __init__(self, alt, az):
        super().__init__()
        self.alt = alt
        self.az = az

    def execute(self, telescope):
        self.state = CMD_RUNNING
        print("[CMD] MoveCommand RUNNING")
        telescope.enqueue_move(self.alt, self.az)

    def update(self, telescope, dt):
        if self.state != CMD_RUNNING:
            return

        if telescope.is_target_reached():
            self.state = CMD_SUCCESS 
            print("[CMD] MoveCommand SUCCESS")

class StopCommand(Command):
    def execute(self, telescope):
        self.state = CMD_ABORTED
        telescope.stop()
