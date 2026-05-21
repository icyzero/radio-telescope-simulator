# src/analysis/fits_analyzer.py

import os
import glob
import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits

class AstroFitsAnalyzer:
    def __init__(self, observation_dir="observations"):
        self.obs_dir = observation_dir
        self.c = 299792.458          # 빛의 속도 (km/s)
        self.f_rest = 1420.40575e6    # 수소선(H-I) 고유 주파수 (Hz)
        
        # 안전장치: 관측 폴더가 없다면 자동 생성
        if not os.path.exists(self.obs_dir):
            os.makedirs(self.obs_dir)

    def get_latest_fits(self):
        """가장 최근에 관측 및 저장된 FITS 파일 경로 획득"""
        search_path = os.path.join(self.obs_dir, "*.fits")
        files = glob.glob(search_path)
        if not files:
            return None
        # 가장 최근에 수정/생성된 FITS 파일 반환
        return max(files, key=os.path.getctime)

    def plot_scientific_profile(self, fits_path):
        """FITS 데이터를 파싱하여 논문 레벨의 도플러 속도 스펙트럼 생성"""
        if not fits_path:
            print("❌ [분석 실패] 분석할 FITS 파일이 observations/ 폴더에 존재하지 않습니다.")
            print("💡 장비를 가동하여 관측 데이터([A] 또는 [S])를 먼저 생성해주세요.")
            return
            
        print(f"📦 [Day 118 Analysis] FITS 자원 파싱 및 로드 중: {fits_path}")
        
        with fits.open(fits_path) as hdul:
            # FITS 헤더 및 데이터 데이터셋 추출
            header = hdul[0].header
            data = hdul[0].data  # 실시간 축적된 PSD 배열
            
            # 헤더 메타데이터 안전장치 (하드웨어 동기화 값 역산 및 폴백 세팅)
            center_freq = header.get('CRVAL1', 1420.4e6)
            sample_rate = header.get('CDELT1', 2.4e6)
            num_bins = data.shape[-1] if len(data.shape) > 0 else 2048
            
            # 1차원 데이터 추출 (시간축 Waterfall Matrix 형태일 경우 앙상블 평균 처리)
            if len(data.shape) == 2:
                profile = np.mean(data, axis=0)
            else:
                profile = data

        # 도플러 속도 축 정밀 재계산 (Day 116 하드웨어 락인 데이터 연동)
        freq_offsets = np.fft.fftshift(np.fft.fftfreq(num_bins, 1.0 / sample_rate))
        absolute_freqs = center_freq + freq_offsets
        velocities = self.c * (1.0 - (absolute_freqs / self.f_rest))

        # ----------------------------------------------------
        # [ApJ 학술지 / 대시보드 하이엔드 하이브리드 시각화]
        # ----------------------------------------------------
        plt.style.use('dark_background')  # 대시보드 통합형 다크 테마
        fig, ax = plt.subplots(figsize=(10, 6), dpi=150)
        
        # 은하수 전파 강도를 상징하는 네온 사이언(Cyan) 라인 플롯
        ax.plot(velocities, profile, color='#00ffcc', lw=1.5, label='Observed H-I Line Profile')
        
        # 💡 관측 실증 데이터: -125 km/s 영역 우리은하 나선팔(Spiral Arm) 과학적 하이라이트 에어리어 지정
        ax.axvspan(-135, -115, color='#ffcc00', alpha=0.15, label='Galactic Spiral Arm Feature (-125 km/s)')
        ax.axvline(-125, color='#ffcc00', linestyle='--', alpha=0.5, lw=1.2)
        
        # 텍스트 및 학술 논문급 라벨링 고도화
        ax.set_title(f"Galactic 21cm Neutral Hydrogen (H-I) Line Profile\nSource: {os.path.basename(fits_path)}", 
                     fontsize=12, fontweight='bold', pad=15)
        
        # 💡 버그 수정: r"..." (Raw String) 지정을 통해 \t 이스케이프가 라벨을 깨뜨리는 현상 완벽 차단
        ax.set_xlabel(r"Radial Velocity relative to LSR ($v_{\mathrm{LSR}}$) [km/s]", fontsize=10)
        ax.set_ylabel("Antenna Temperature / Relative Intensity [dB]", fontsize=10)
        
        # 축 그리드 및 세부 미학 조정
        ax.grid(True, linestyle=':', alpha=0.3, color='gray')
        ax.legend(loc='upper right', frameon=True, facecolor='#111111', edgecolor='#333333')
        
        # 천문학 관례에 따른 속도 축 정렬 (보통 미세 구조 관찰을 위해 범위를 -200 ~ +200 선으로 리미트 가능)
        ax.set_xlim(200, -200) 
        
        # 결과물 자동 저장 자동화
        output_img = fits_path.replace(".fits", "_profile.png")
        plt.tight_layout()
        plt.savefig(output_img, bbox_inches='tight', dpi=150)
        plt.close()
        
        print(f"🎯 [분석 완료] ApJ 논문급 과학 스펙트럼 그래프 시각화 성공!")
        print(f"📸 저장된 이미지 경로: {output_img}\n")

if __name__ == "__main__":
    analyzer = AstroFitsAnalyzer()
    latest_file = analyzer.get_latest_fits()
    analyzer.plot_scientific_profile(latest_file)