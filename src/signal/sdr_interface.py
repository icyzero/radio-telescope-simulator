#src/signal/sdr_interface.py

import numpy as np
import time

try:
    from rtlsdr import RtlSdr
    HAS_REAL_SDR = True
except ImportError:
    HAS_REAL_SDR = False

class VirtualSDR:
    def __init__(self, sample_rate=2.4e6):
        self.fs = sample_rate
        self.gain = 10.0  # 가상 게인(Gain) 설정
        print(f"DEBUG: VirtualSDR initialized at {self.fs/1e6} MHz")

    def read_samples(self, num_samples=2048):
        t = np.arange(num_samples) / self.fs
        # Gain 값을 반영하여 신호 강도 조절 (기존 1j -> self.gain * 1j)
        freq = 500000 + 200000 * np.sin(time.time() * 2)
        signal = self.gain * np.exp(1j * 2 * np.pi * freq * t)
        noise = (np.random.randn(num_samples) + 1j * np.random.randn(num_samples))
        return signal + noise

    def set_gain(self, gain_val):
        self.gain = max(1.0, gain_val) # 최소값 1 유지
        print(f"📡 [Virtual] Gain set to: {self.gain}")

class SDRFactory:
    @staticmethod
    def get_sdr(mode="auto", sample_rate=2.4e6, center_freq=1420.4e6):
        # 1. 실제 장비 모드 시도
        if mode in ["real", "auto"] and HAS_REAL_SDR:
            try:
                sdr = RtlSdr()
                sdr.sample_rate = sample_rate
                sdr.center_freq = center_freq
                sdr.gain = 'auto'
                print(f"📡 [REAL] SDR Connected: {center_freq/1e6} MHz")
                return sdr
            except Exception as e:
                if mode == "real": raise e
                print(f"⚠️ 장비 연결 실패 ({e}). 가상 모드로 전환합니다.")

        # 2. 가상 모드 반환
        return VirtualSDR(sample_rate)

class SignalProcessor:
    """받은 데이터를 분석하여 스펙트럼을 계산하는 클래스"""
    def __init__(self):
        self.history = None

    @staticmethod
    def get_power_spectrum(samples):
        # 1. Windowing (누설 현상 방지)
        windowed = samples * np.blackman(len(samples))
        # 2. FFT 수행
        fft_data = np.fft.fftshift(np.fft.fft(windowed))
        # 3. Power (절대값의 제곱) 계산
        power = np.abs(fft_data) ** 2
        return power
    
    def smooth_spectrum(self, new_psd, alpha=0.2):
        """지수 이동 평균을 이용한 신호 평활화"""
        if self.history is None or self.history.shape != new_psd.shape:
            self.history = new_psd.copy()
        else:
            # alpha가 작을수록 더 부드럽지만 반응 속도는 느려짐
            self.history = (alpha * new_psd) + (1 - alpha) * self.history
        return self.history

# [Day 101 Test]
sdr = VirtualSDR()
proc = SignalProcessor()

samples = sdr.read_samples(2048)
spectrum = proc.get_power_spectrum(samples)

print(f"Captured {len(samples)} samples. Peak power detected!")