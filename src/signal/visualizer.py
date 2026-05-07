# src/signal/visualizer.py

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from src.data.recorder import FitsRecorder

class SpectrumVisualizer:
    def __init__(self, sdr, processor, interval=50): # 갱신 속도를 50ms로 높여 더 부드럽게 설정
        self.sdr = sdr
        self.processor = processor
        self.interval = interval
        self.history = None
        
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

class WaterfallVisualizer:
    def __init__(self, sdr, processor, interval=50, history_size=100):
        self.sdr = sdr
        self.processor = processor
        self.interval = interval
        self.history_size = history_size
        self.fs = sdr.fs
        num_samples = 2048
        
        plt.style.use('dark_background')
        # 1. 2단 레이아웃 설정
        self.fig, (self.ax_spec, self.ax_water) = plt.subplots(2, 1, figsize=(9, 7), sharex=True)

        self.recorder = FitsRecorder()
        self.fig.canvas.mpl_connect('key_press_event', self.on_key)
        
        # 2. 상단: Spectrum Line
        self.line, = self.ax_spec.plot([], [], lw=1, color='#00ff00')
        self.ax_spec.set_ylim(-50, 70)
        self.ax_spec.set_ylabel("Power (dB)")
        self.ax_spec.set_title("🌌 Real-time Radio Analysis")

        # 3. 하단: Waterfall Image
        # 2D 버퍼 초기화 (시간 x 주파수)
        self.waterfall_buffer = np.full((self.history_size, num_samples), -50.0)
        self.img = self.ax_water.imshow(
            self.waterfall_buffer, 
            aspect='auto', 
            cmap='magma', # 전파 강도를 표현하기 좋은 색상
            vmin=-30, vmax=50,
            extent=[-self.fs/2/1e6, self.fs/2/1e6, self.history_size, 0]
        )
        self.ax_water.set_xlabel("Frequency Offset (MHz)")
        self.ax_water.set_ylabel("Time History (Frames)")

    def on_key(self, event):
        if event.key == 's' or event.key == 'S':
            # 현재 망원경 상태 메타데이터 (예시)
            meta = {
                'az': 120.0, 
                'el': 45.0, 
                'center_freq': 1420.4,
                'sample_rate': self.fs
            }
            # 현재까지 쌓인 Waterfall 버퍼 저장
            self.recorder.save_observation(self.waterfall_buffer, meta)

    def update(self, frame):
        samples = self.sdr.read_samples(2048)
        raw_psd = self.processor.get_power_spectrum(samples)
        
        # [Day 103 신기능] 신호 평활화 적용
        psd = self.processor.smooth_spectrum(raw_psd, alpha=0.15)
        db_psd = 10 * np.log10(psd + 1e-12)
        
        # 주파수 축 계산
        freqs = np.fft.fftshift(np.fft.fftfreq(len(samples), 1/self.fs)) / 1e6
        
        # 상단 그래프 업데이트
        self.line.set_data(freqs, db_psd)
        
        # 하단 Waterfall 업데이트: 데이터를 위로 한 칸씩 밀고 맨 아래에 새 데이터 삽입
        self.waterfall_buffer = np.roll(self.waterfall_buffer, -1, axis=0)
        self.waterfall_buffer[-1, :] = db_psd
        self.img.set_array(self.waterfall_buffer)
        
        return self.line, self.img

    def show(self):
        self.ani = FuncAnimation(self.fig, self.update, interval=self.interval, blit=True)
        plt.tight_layout()
        plt.show()