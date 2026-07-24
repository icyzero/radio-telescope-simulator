# src/scheduler/observation_manager.py

"""sdr장비 연동"""
from src.signal.sdr_interface import VirtualSDR, SignalProcessor
from src.utils.logger import log


class ObservationManager:
    """SDR 장비 연동 및 데이터 처리 전담"""
    def __init__(self, controller):
        self.controller = controller
        self.sdr = VirtualSDR()
        self.proc = SignalProcessor()

    def take_data(self, manager_name):
        mgr = self.controller.managers.get(manager_name)

        # 망원경이 정지 상태(IDLE)일 때만 샘플링
        if mgr and mgr.telescope.state.name == "IDLE":
            samples = self.sdr.read_samples(2048)
            return self.proc.get_power_spectrum(samples)

        log(f"[SIGNAL] Capture failed: Telescope is {mgr.telescope.state.name if mgr else 'NONE'}")
        return None