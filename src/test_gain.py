# src/test_gain.py

import os
# DLL 최우선 주입 (RTL-SDR V4 드라이버 로드)
os.add_dll_directory(r"D:\radio-telescope-simulator")

import numpy as np
import time
from rtlsdr import RtlSdr

def scan_wireless_environment():
    print("\n📡 [Day 115] Gain 최적화 및 주변 RFI(전파 간섭) 환경 스캔 시작")
    print("================================================================")
    
    try:
        sdr = RtlSdr()
    except Exception as e:
        print(f"❌ SDR 장비를 찾을 수 없습니다. 연결 상태를 확인하세요! ({e})")
        return

    sdr.sample_rate = 2.4e6
    sdr.center_freq = 1420.4e6  # 실제 수소선 타겟 주파수 설정
    
    # 💡 보완 1: 일부 개발 환경에서 valid_gains가 비어있거나 에러 날 때를 대비한 예외 처리
    try:
        supported_gains = sdr.valid_gains
        if len(supported_gains) == 0:
            supported_gains = [0.0, 3.7, 7.7, 11.8, 15.7, 19.7, 22.9, 25.4, 28.0, 32.8, 37.2, 40.2, 44.5, 49.6]
    except Exception:
        supported_gains = [0.0, 3.7, 7.7, 11.8, 15.7, 19.7, 22.9, 25.4, 28.0, 32.8, 37.2, 40.2, 44.5, 49.6]
        
    print(f"💡 지원되는 하드웨어 Gain 목록: {supported_gains}\n")
    
    best_gain = None
    max_optimal_power = float('-inf') # 가장 신호 대 잡음비가 좋은 지점을 찾기 위함
    
    print(f"{'Gain (dB)':<10} | {'평균 파워 (dB)':<15} | {'상태 (Status)':<15}")
    print("-" * 50)
    
    for g in supported_gains:
        sdr.gain = g
        time.sleep(0.05) # 증폭기 회로 안정화 대기
        
        # 💡 보완 2: 하드웨어 게인이 바뀐 직후 처음 들어오는 1~2개의 샘플 버퍼에는 
        # 이전 게인의 잔류 신호나 일시적 튀는 회로 잡음이 섞입니다. (Flush Buffer)
        _ = sdr.read_samples(1024) 
        
        # 실제 분석용 샘플 수집 및 DC 오프셋 제거 필터 적용 (Day 114 수식)
        raw = sdr.read_samples(2048)
        clean = (raw.real - np.mean(raw.real)) + 1j * (raw.imag - np.mean(raw.imag))
        
        # 전체 신호의 평균 전력 계산
        power = 10 * np.log10(np.mean(np.abs(clean) ** 2) + 1e-12)
        
        # 💡 보완 3: pyrtlsdr의 샘플 최대 진폭 기반 포화 감지 정밀화
        # 수신된 복소수 샘플의 절대값 크기가 IQ ADC 한계선(보통 1.0 전후)에 근접하는지 체크
        max_val = np.max(np.abs(clean))
        
        if max_val > 0.95:
            status = "⚠️ 포화 (Saturation)"
        elif power < -35: # 관측실 환경에 따라 하한선 조정
            status = "📉 신호 미약"
        else:
            status = "✅ 양호 (Optimal)"
            # 포화되지 않는 양호한 구간 중, 가장 전력이 잘 밀려 올라오는 최적값 갱신
            if power > max_optimal_power:
                max_optimal_power = power
                best_gain = g
            
        print(f"{g:<10.1f} | {power:<15.2f} | {status}")
        
    print("================================================================")
    if best_gain is not None:
        print(f"🎯 최적의 하드웨어 관측 골디락스 Gain 결정: {best_gain} dB")
    else:
        print("⚠️ 환경 노이즈가 너무 강하거나 약합니다! Gain을 'auto'로 권장합니다.")
        
    sdr.close()

if __name__ == "__main__":
    scan_wireless_environment()