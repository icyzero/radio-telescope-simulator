# src/signal/sdr_interface.py

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
        self.sample_rate = sample_rate # 💡 수정: 외부 헬스 체크 컴포넌트와의 속성 이름 호환성 확보
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
        if samples is None or len(samples) == 0:
            return np.zeros(2048)

        # ----------------------------------------------------
        # [Day 114: 하드웨어 고유 DC 오프셋(정중앙 기둥 노이즈) 제거 필터]
        # ----------------------------------------------------
        # IQ 샘플 복소수 배열에서 실수부(I)와 허수부(Q)의 평균값(직류 성분)을 도출합니다.
        dc_i = np.mean(samples.real)
        dc_q = np.mean(samples.imag)
        
        # 원본 신호에서 직류 편향 성분을 차감하여 정중앙의 가짜 유령 세로줄을 제거합니다.
        clean_samples = (samples.real - dc_i) + 1j * (samples.imag - dc_q)
        # ----------------------------------------------------

        # 1. Windowing (누설 현상 및 사이드 로브 억제를 위해 깨끗해진 샘플에 블랙맨 창 적용)
        windowed = clean_samples * np.blackman(len(clean_samples))
        
        # 2. FFT 수행 (주파수 도메인 변환)
        fft_data = np.fft.fftshift(np.fft.fft(windowed))
        
        # 3. Power Density (절대값의 제곱) 계산
        power = np.abs(fft_data) ** 2
        return power
    
    def smooth_spectrum(self, new_psd, alpha=0.2):
        """지수 이동 평균(EMA)을 이용한 실시간 신호 평활화"""
        if self.history is None or self.history.shape != new_psd.shape:
            self.history = new_psd.copy()
        else:
            # alpha가 작을수록 파형이 부드러워지며, 우주 배경 잡음 속에서 미약한 신호를 판별하기 좋아집니다.
            self.history = (alpha * new_psd) + (1 - alpha) * self.history
        return self.history

# 💡 안전조치: 다른 파일에서 import할 때 아래 일회성 테스트 코드가 실행되지 않도록 가둠
if __name__ == "__main__":
    # [Day 101 Test]
    sdr = VirtualSDR()
    proc = SignalProcessor()

    samples = sdr.read_samples(2048)
    spectrum = proc.get_power_spectrum(samples)

    print(f"Captured {len(samples)} samples. Peak power detected!")