class Command: #명령에 '시간'을 붙일 수 있는 구조 
    def execute(self, telescope):
        raise NotImplementedError
    
class MoveCommand(Command):
    def __init__(self, alt, az):
        self.alt = alt
        self.az = az

    def execute(self, telescope):
        telescope.enqueue_move(self.alt, self.az)

class StopCommand(Command):
    def execute(self, telescope):
        telescope.stop()
