# src/signal/visualizer.py

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

class SpectrumVisualizer:
    def __init__(self, sdr, processor, interval=50): # 갱신 속도를 50ms로 높여 더 부드럽게 설정
        self.sdr = sdr
        self.processor = processor
        self.interval = interval
        
        # 1. 그래프 디자인 (다크 모드 스타일로 전파 관측 느낌 강조)
        plt.style.use('dark_background')
        self.fig, self.ax = plt.subplots(figsize=(12, 6))
        self.line, = self.ax.plot([], [], lw=1.5, color='#33ff33') # 네온 그린
        
        # 2. 물리적 축 설정 (SDR 사양 반영)
        self.fs = sdr.fs
        self.ax.set_xlim(-self.fs/2 / 1e6, self.fs/2 / 1e6) 
        self.ax.set_ylim(-50, 70) # 로그 스케일이므로 음수 대역까지 표현
        self.ax.set_xlabel("Frequency Offset (MHz)", fontsize=12)
        self.ax.set_ylabel("Power Density (dB)", fontsize=12)
        self.ax.set_title("🌌 Real-time Radio Spectrum Analyzer", fontsize=15, pad=20)
        self.ax.grid(True, color='gray', linestyle='--', alpha=0.3)

    def init_plot(self):
        self.line.set_data([], [])
        return self.line,

    def update(self, frame):
        # [Day 101 로직 연동]
        samples = self.sdr.read_samples(2048)
        psd = self.processor.get_power_spectrum(samples)
        
        # [핵심] 로그 스케일 변환: 1,000,000배 차이를 60dB 차이로 압축
        db_psd = 10 * np.log10(psd + 1e-12)
        
        # 주파수 축 계산 (FFT 결과와 매칭)
        freqs = np.fft.fftshift(np.fft.fftfreq(len(samples), 1/self.fs)) / 1e6
        
        self.line.set_data(freqs, db_psd)
        return self.line,

    def show(self):
        self.ani = FuncAnimation(self.fig, self.update, init_func=self.init_plot,
                                 interval=self.interval, blit=True)
        plt.show()