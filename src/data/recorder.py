#src/data/recorder.py

import os
import time
import numpy as np
from astropy.io import fits

class FitsRecorder:
    def __init__(self, output_dir="observations"):
        # 기존 변수명(output_dir) 및 기본 디렉토리 보존
        self.output_dir = output_dir
        
        # 📂 [Day 124] 천체별 관측 데이터 하위 저장 폴더 맵핑
        self.target_subdirs = {
            "MILKY_WAY_H1": "milkyway",
            "SOLAR_BURST": "solar",
            "JUPITER_DAM": "jupiter"
        }

    def save_observation(self, data, metadata):
        """
        data: 2D Waterfall Array (Time x Frequency)
        metadata: 망원경 상태 정보 및 현재 활성화된 천체 프로필 정보 통합 딕셔너리
        """
        print(f"\n💾 [FitsRecorder] FITS 데이터 세분화 아카이빙 시퀀스 개시")
        
        # 1. 메타데이터에서 현재 타겟 키 및 프로필 추출 (없으면 기본값 은하수)
        target_key = metadata.get('target_key', 'MILKY_WAY_H1')
        target_name = metadata.get('target_name', 'Milky Way Neutral Hydrogen (H-I)')
        center_freq = metadata.get('center_freq', 1420.4e6)
        sample_rate = metadata.get('sample_rate', 2.4e6)
        current_gain = metadata.get('gain', 49.6)
        
        # 2. 경로 자동 분기 및 디렉토리 생성 안전장치
        sub_dir = self.target_subdirs.get(target_key, "misc")
        save_path = os.path.join(self.output_dir, sub_dir)
        os.makedirs(save_path, exist_ok=True)
        
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(save_path, f"obs_{target_key}_{timestamp}.fits")

        # 3. HDU(Header Data Unit) 생성 및 데이터 배열화
        if data is None or len(data) == 0:
            data = np.zeros((100, 256)) # 데이터 유실 방지용 폴백
            
        hdu = fits.PrimaryHDU(data)
        hdr = hdu.header

        # 4. [Day 124 핵심] 기존 헤더 보존 + 천문 표준 가변 메타데이터 인젝션
        hdr['DATE-OBS'] = (time.strftime("%Y-%m-%dT%H:%M:%S"), 'Observation start time (UTC)')
        hdr['INSTRUME'] = ('RTL-SDR Blog V4', 'Receiver Hardware Model')
        hdr['OBJECT'] = (target_name, 'Target Astronomical Object')
        
        # 기존 레거시 키와 정밀 물리 키 크로스 매핑
        hdr['FREQ-MHZ'] = (center_freq / 1e6, 'Center Frequency in MHz')
        hdr['CRVAL1'] = (float(center_freq), 'Central Frequency (Hz)')
        hdr['SAMPRATE'] = (float(sample_rate), 'Sample Rate in Hz')
        hdr['CDELT1'] = (float(sample_rate), 'Bandwidth / Sample Rate (Hz)')
        
        # 기존 모터 위치 메타데이터 승계
        hdr['AZIMUTH'] = (metadata.get('az', 0.0), 'Telescope Azimuth')
        hdr['ELEVATIO'] = (metadata.get('el', 0.0), 'Telescope Elevation')
        hdr['GAIN'] = (float(current_gain), 'Locked Hardware Gain in dB')
        hdr['UNIT'] = ('dB', 'Power unit in decibels')

        # 📡 천체 특성에 따른 물리 축 성격 정의 (FITS 전파천문학 표준 규격화)
        if target_key == "MILKY_WAY_H1":
            hdr['CTYPE1'] = ('VELOCITY-LSR', 'Doppler Line-of-Sight Velocity Scale')
            hdr['RESTFREQ'] = (1420405750.0, 'HI Rest Frame Frequency (Hz)')
        elif target_key == "SOLAR_BURST":
            hdr['CTYPE1'] = ('FREQ-DYNAMIC', 'Time-Variable Frequency Drift Scale')
            hdr['DSP_MODE'] = ('DYNAMIC_WATERFALL', 'Solar Type-III Burst Tracker')
        elif target_key == "JUPITER_DAM":
            hdr['CTYPE1'] = ('TIME-SERIES', 'High-Speed Amplitude Power Scale')
            hdr['DSP_MODE'] = ('FAST_TIME_SERIES', 'Io-Interacted S-Burst Capture')

        # 5. 물리적 디스크 저장 완료
        hdu.writeto(filename, overwrite=True)
        print(f"✅ [RECORDER] Data archived: {filename}")
        print(f"📝 [Header Report] OBJECT: {hdr['OBJECT']} | CTYPE1: {hdr['CTYPE1']}")
        print("-" * 70)
        
        return filename