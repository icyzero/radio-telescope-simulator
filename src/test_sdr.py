import os
# 이 치트키가 있으면 프로젝트 폴더 안의 진짜 'rtlsdr.dll'을 낚아챕니다.
os.add_dll_directory(r"D:\radio-telescope-simulator")

from rtlsdr import RtlSdr

try:
    print("시스템 전역 환경에서 SDR 연결을 시도합니다...")
    sdr = RtlSdr()
    sdr.sample_rate = 2.4e6
    sdr.center_freq = 95.1e6
    
    samples = sdr.read_samples(1024)
    print(f"🎯 [전역 환경 성공] 실제 데이터 {len(samples)} 개 수신 완료!")
    sdr.close()
except Exception as e:
    print(f"❌ 전역 환경 실패: {e}")