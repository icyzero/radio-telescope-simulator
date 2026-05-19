# src/test_doppler.py

import os
# 전역 환경 대응을 위한 DLL 드라이버 주입
os.add_dll_directory(r"D:\radio-telescope-simulator")

import numpy as np
from rtlsdr import RtlSdr

class DopplerAstroEngine:
    def __init__(self, center_freq=1420.4e6, sample_rate=2.4e6):
        self.center_freq = center_freq
        self.sample_rate = sample_rate
        self.c = 299792.458  # 빛의 속도 (km/s)
        self.f_rest = 1420.40575e6  # 수소선 고유 주파수 (Hz)

    def calculate_velocity_axis(self, num_bins=2048):
        """FFT 빈(Bin) 주파수 배열을 은하 가스 속도(km/s) 배열로 직접 변환"""
        # 1. 각 FFT 빈의 상대 주파수 계산 (중앙이 center_freq)
        freq_offsets = np.fft.fftshift(np.fft.fftfreq(num_bins, 1.0 / self.sample_rate))
        absolute_freqs = self.center_freq + freq_offsets
        
        # 2. 도플러 효과 공식을 적용하여 속도(km/s)로 역산
        # v = c * (1.0 - f_obs / f_rest)
        # f_obs > f_rest 이면 음수(다가옴, 청색편이), f_obs < f_rest 이면 양수(멀어짐, 적색편이)
        velocities = self.c * (1.0 - (absolute_freqs / self.f_rest))
        return velocities, absolute_freqs

def run_astro_observation():
    print("\n📡 [Day 116] 실전 은하 수소선 도플러 속도 변환 관측 개시")
    print("================================================================")
    
    engine = DopplerAstroEngine(center_freq=1420.4e6, sample_rate=2.4e6)
    v_axis, f_axis = engine.calculate_velocity_axis(2048)
    
    # 하드웨어 연결 안전 장치
    try:
        sdr = RtlSdr()
    except Exception as e:
        print(f"❌ SDR 하드웨어를 가동할 수 없습니다. 연결을 확인하세요. ({e})")
        return
        
    sdr.sample_rate = 2.4e6
    sdr.center_freq = 1420.4e6
    sdr.gain = 49.6  # Day 115에서 도출한 골디락스 고정 게인 락(Lock) 적용
    
    # 안정화 버퍼 비우기 및 실제 샘플 로드
    _ = sdr.read_samples(1024)
    raw = sdr.read_samples(2048)
    sdr.close()
    
    # Day 114 고급 DSP: DC 오프셋 클리닝 필터 고속 연산
    clean = (raw.real - np.mean(raw.real)) + 1j * (raw.imag - np.mean(raw.imag))
    
    # FFT 및 중심 주파수 정렬(fftshift)
    fft_data = np.fft.fftshift(np.fft.fft(clean))
    psd = 10 * np.log10(np.abs(fft_data) ** 2 + 1e-12)
    
    print(f"✅ 관측 밴드범위: {f_axis[0]/1e6:.2f} MHz ~ {f_axis[-1]/1e6:.2f} MHz")
    # 물리적 해석 가이드 라벨 보완
    print(f"🌌 가스 속도 해상도 밴드:")
    print(f"   - 좌측 끝 (최대 주파수 영역): {v_axis[0]:.1f} km/s")
    print(f"   - 우측 끝 (최소 주파수 영역): {v_axis[-1]:.1f} km/s")
    print("-" * 64)
    
    # 정중앙 관측 기준점 프로파일 출력
    center_idx = len(psd) // 2
    print("🎯 [실시간 도플러 스펙트럼 프로파일 스냅샷]")
    
    # 세 지점의 속도 포인트 매핑 상태 스캔 출력 (주파수 상승 -> 속도 감소 경향 확인용)
    for i in [center_idx - 10, center_idx, center_idx + 10]:
        shift_type = "🔵 다가옴(청색)" if v_axis[i] < 0 else "🔴 멀어짐(적색)"
        if abs(v_axis[i]) < 1.0: shift_type = "🟢 정지정점(기준)"
            
        print(f"주파수: {f_axis[i]/1e6:.4f} MHz | 속도: {v_axis[i]:>7.2f} km/s ({shift_type}) | 파워: {psd[i]:.2f} dB")
        
    print("================================================================")
    print("✅ 실제 관측 데이터에 천문학적 도플러 스케일 맵핑 성공!")

if __name__ == "__main__":
    run_astro_observation()