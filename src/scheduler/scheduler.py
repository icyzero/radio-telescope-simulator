class SystemController:
    def __init__(self):
        self.managers = {}
        self.mode = "NORMAL" #정책만 분기, 흐름 침범X

    def register_manager(self, name, manager):
        self.managers[name] = manager

    def update(self, dt):
        # 전역 정책 판단 위치
        for manager in self.managers.values():
            manager.update(dt)

    def global_stop(self):
        for manager in self.managers.values():
            manager.local_stop()
