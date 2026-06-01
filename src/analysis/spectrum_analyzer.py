# src/analysis/spectrum_analyzer.py

import os
import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits

class AstroSpectrumAnalyzer:
    def __init__(self, base_dir="observations"):
        self.base_dir = base_dir

    def plot_before_after_comparison(self, raw_file_name, stacked_file_name, target_subdir="milkyway"):
        """
        [Day 129 핵심] 단일 관측 데이터(Before)와 텐서 적분 데이터(After)를
        동시에 파싱하여 $\sqrt{N}$ 노이즈 상쇄 효과를 시각적으로 정밀 비교 분석합니다.
        """
        raw_path = os.path.join(self.base_dir, target_subdir, raw_file_name)
        stacked_path = os.path.join(self.base_dir, target_subdir, "stacked", stacked_file_name)
        
        print(f"\n📊 [Day 129 Analyzer] 비포/애프터 과학 스펙트럼 비교 시각화 개시")
        print(f" 🔴 Raw Source   : {raw_path}")
        print(f" 🟢 Stacked Master: {stacked_path}")
        print("-" * 75)
        
        # 1. 두 FITS 파일 데이터 파싱
        if not os.path.exists(raw_path) or not os.path.exists(stacked_path):
            print("❌ [Analyzer Error] 비교 연산에 필요한 FITS 파일이 누락되었습니다.")
            print("💡 팁: 관측(Manual Save)을 수행하고 stacker.py를 먼저 가동해 주세요.")
            return

        with fits.open(raw_path) as hdul_raw, fits.open(stacked_path) as hdul_stacked:
            raw_data = hdul_raw[0].data
            stacked_data = hdul_stacked[0].data
            
            raw_header = hdul_raw[0].header
            stacked_header = hdul_stacked[0].header

        # 2. 2차원 워터폴 버퍼에서 1차원 평균 스펙트럼 벡터 추출
        raw_spectrum = np.mean(raw_data, axis=0) if raw_data.ndim > 1 else raw_data
        stacked_spectrum = np.mean(stacked_data, axis=0) if stacked_data.ndim > 1 else stacked_data
        
        # X축 축 정보 계산 (샘플 레이트 및 주파수 기반 픽셀 바인딩)
        bins = len(raw_spectrum)
        sample_rate = raw_header.get('CDELT1', 2.4e6)
        freq_axis = np.linspace(-sample_rate/2, sample_rate/2, bins) / 1e6 # MHz 단위 변환
        
        # 3. 고급 학술지 규격의 2단 비교 그래프 생성
        plt.style.use('dark_background')
        fig, axes = plt.subplots(2, 1, figsize=(11, 7), sharex=True)
        fig.suptitle(f"[REPORT] Galactic H-I Line Signal Restoration Report ({raw_header.get('OBJECT', 'Unknown')})", 
                     fontsize=14, fontweight='bold', color='cyan')

        # 🔴 Subplot 1: 스택 전 날것의 단일 관측 데이터 (거친 노이즈 부각)
        axes[0].plot(freq_axis, raw_spectrum, color='crimson', alpha=0.8, linewidth=1, label='Single Raw Frame (Before)')
        axes[0].set_title(f"[BEFORE] Raw Observation Snapshot [Gain: {raw_header.get('GAIN', 49.6)} dB]", fontsize=11, color='orange')
        axes[0].set_ylabel("Power Spectral Density (dB)", fontsize=10)
        axes[0].grid(True, linestyle='--', alpha=0.3, color='gray')
        axes[0].legend(loc='upper right')

        # 🟢 Subplot 2: 텐서 스택 연산이 끝난 마스터 과학 데이터 (매끄러운 신호 복원)
        axes[1].plot(freq_axis, stacked_spectrum, color='limegreen', alpha=0.9, linewidth=1.5, label=f"Stacked Master Frame (N={stacked_header.get('STACK_N', 3)})")
        axes[1].fill_between(freq_axis, stacked_spectrum, np.min(stacked_spectrum), color='green', alpha=0.15)
        
        # 💡 보정: color='lightgrid' 에러를 'lightgray'로 안전하게 변경
        axes[1].set_title(f"[AFTER] Mathematical $\\sqrt{{N}}$ Noise-Cancelled Spectrum (After)", fontsize=11, color='lightgray')
        axes[1].set_xlabel("Offset Frequency from Central LO (MHz)", fontsize=10)
        axes[1].set_ylabel("Power Spectral Density (dB)", fontsize=10)
        axes[1].grid(True, linestyle='--', alpha=0.3, color='gray')
        axes[1].legend(loc='upper right')

        # 통계적 수치 오버레이 박스 주입
        stack_n = stacked_header.get('STACK_N', 3)
        avg_snr = stacked_header.get('AVG_SNR', 0.0)
        # 수학적 백색 잡음 상쇄율 역산 ($\sqrt{N}$ 기반 이론치 계산 오버레이)
        theoretical_reduction = (1.0 - (1.0 / np.sqrt(stack_n))) * 100
        
        text_info = f"Stacked Frames: {stack_n}\nAvg Input SNR: {avg_snr:.2f} dB\nNoise Reduction: ~{theoretical_reduction:.1f}%"
        props = dict(boxstyle='round,pad=0.5', facecolor='black', alpha=0.7, edgecolor='lime')
        axes[1].text(0.02, 0.93, text_info, transform=axes[1].transAxes, fontsize=9.5,
                     verticalalignment='top', bbox=props, color='white', fontfamily='monospace')

        plt.tight_layout(rect=[0, 0, 1, 0.96])
        
        # 결과 이미지 영구 보관 저장
        output_dir = os.path.join(self.base_dir, target_subdir, "stacked")
        os.makedirs(output_dir, exist_ok=True)
        output_img_path = os.path.join(output_dir, "Spectrum_Restoration_Report.png")
        
        plt.savefig(output_img_path, dpi=300)
        print(f"✅ 논문급 비교 분석 보고서 이미지 저장 완료!")
        print(f" 📸 그래픽 경로: {output_img_path}")
        print("=" * 75)
        plt.show()

if __name__ == "__main__":
    analyzer = AstroSpectrumAnalyzer()
    
    # Day 127에 확인한 실제 파일명 리스트를 매핑합니다.
    raw_sample = "obs_MILKY_WAY_H1_20260530_130040.fits"
    master_sample = "Master_Stacked_Science_Data.fits"
    
    analyzer.plot_before_after_comparison(raw_sample, master_sample)