# src/analysis/inspector.py

from astropy.io import fits
import numpy as np
import matplotlib.pyplot as plt

class FitsInspector:
    def __init__(self, filepath):
        try:
            self.hdul = fits.open(filepath)
            self.data = self.hdul[0].data
            self.header = self.hdul[0].header
            print(f"✅ Successfully loaded: {filepath}")
        except FileNotFoundError:
            print(f"❌ Error: File {filepath} not found.")
            raise

    def analyze_signal(self):
        # 1. 각 시간대별(행) 최대 강도를 가진 인덱스(열) 추출
        # 이것이 바로 우리가 눈으로 보던 '뱀'의 척추입니다.
        peaks = np.argmax(self.data, axis=1)
        
        # 2. SNR(신호 대 잡음비) 간단 계산
        # 전체 평균(노이즈) 대비 피크값의 비율
        avg_noise = np.mean(self.data)
        peak_val = np.max(self.data)
        snr = peak_val - avg_noise # dB 단위이므로 뺄셈으로 계산
        
        # 3. 리포트 출력
        print(f"\n--- 📋 Scientific Analysis Report ---")
        print(f"Obs Date   : {self.header.get('DATE-OBS', 'N/A')}")
        print(f"Instrument : {self.header.get('INSTRUME', 'N/A')}")
        print(f"Center Freq: {self.header.get('FREQ-MHZ', 'N/A')} MHz")
        print(f"Peak SNR   : {snr:.2f} dB")
        
        # 4. 드리프트 폭 계산
        drift_range = np.max(peaks) - np.min(peaks)
        print(f"Drift Range: {drift_range} bins")
        
        return peaks

    def plot_analysis(self, peaks):
        # 원본 데이터와 추적된 경로를 동시에 비교
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # 좌측: 원본 폭포수 데이터
        ax1.imshow(self.data, aspect='auto', cmap='magma')
        ax1.set_title("Original Waterfall Data")
        ax1.set_ylabel("Time (Frames)")
        
        # 우측: 추적된 신호 경로 (Scatter plot)
        ax2.plot(peaks, range(len(peaks)), color='cyan', lw=2)
        ax2.invert_yaxis() # 시간을 위에서 아래로 흐르게 일치
        ax2.set_title("Tracked Signal Path (Peak Tracking)")
        ax2.set_xlabel("Frequency Bin Index")
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()