#src/signal/sdr_interface.py

import numpy as np
import time

class VirtualSDR:
    """SDR 장비를 대신하여 가상의 IQ 데이터를 생성하는 클래스"""
    def __init__(self, sample_rate=2.4e6): # 2.4 MHz
        self.fs = sample_rate

    def read_samples(self, num_samples=1024):
        # 1. 시간 축 생성
        t = np.arange(num_samples) / self.fs
        
        # 2. 가상의 신호 (주파수 이동된 신호 모사)
        """target_freq = 500000 # 500kHz 지점에서 신호 발생
        iq_signal = np.exp(1j * 2 * np.pi * target_freq * t)"""
        dynamic_freq = 500000 + 200000 * np.sin(time.time() * 2)# 시간에 따라 주파수가 왔다갔다하게 만듦 (지그재그 신호)
        iq_signal = np.exp(1j * 2 * np.pi * dynamic_freq * t)
        
        # 3. 우주 배경 복사 노이즈 추가
        noise = (np.random.randn(num_samples) + 1j * np.random.randn(num_samples)) * 0.5
        return iq_signal + noise

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