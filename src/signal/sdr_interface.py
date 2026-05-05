#src/signal/sdr_interface.py

import numpy as np

class VirtualSDR:
    """SDR 장비를 대신하여 가상의 IQ 데이터를 생성하는 클래스"""
    def __init__(self, sample_rate=2.4e6): # 2.4 MHz
        self.fs = sample_rate

    def read_samples(self, num_samples=1024):
        # 1. 시간 축 생성
        t = np.arange(num_samples) / self.fs
        
        # 2. 가상의 신호 (주파수 이동된 신호 모사)
        target_freq = 500000 # 500kHz 지점에서 신호 발생
        iq_signal = np.exp(1j * 2 * np.pi * target_freq * t)
        
        # 3. 우주 배경 복사 노이즈 추가
        noise = (np.random.randn(num_samples) + 1j * np.random.randn(num_samples)) * 0.5
        return iq_signal + noise

class SignalProcessor:
    """받은 데이터를 분석하여 스펙트럼을 계산하는 클래스"""
    @staticmethod
    def get_power_spectrum(samples):
        # 1. Windowing (누설 현상 방지)
        windowed = samples * np.blackman(len(samples))
        # 2. FFT 수행
        fft_data = np.fft.fftshift(np.fft.fft(windowed))
        # 3. Power (절대값의 제곱) 계산
        power = np.abs(fft_data) ** 2
        return power

# [Day 101 Test]
sdr = VirtualSDR()
proc = SignalProcessor()

samples = sdr.read_samples(2048)
spectrum = proc.get_power_spectrum(samples)

print(f"Captured {len(samples)} samples. Peak power detected!")