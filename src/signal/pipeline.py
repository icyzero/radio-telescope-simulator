# src/signal/pipeline.py

import time
import random
import numpy as np

class MockTargetProfile:
    """테스트 구동을 위한 가상 천체 프로필 객체"""
    def __init__(self):
        self.sample_rate = 2400000  # 2.4 MHz
        self.center_freq = 1420405750.0  # H-I Line

class ResilientSignalPipeline:
    def __init__(self, sdr_manager=None):
        self.sdr_manager = sdr_manager
        self.is_running = True
        self.max_retries = 5  # 최대 핫플러그 재연결 시도 횟수

    def start_resilient_stream(self, target_key="milkyway", target_profile=None):
        """
        [Day 132 핵심] 하드웨어 유실 및 RFI 크래시로부터 메인 프로세스를 보호하고,
        지수 백오프 알고리즘을 가동하여 안테나를 핫플러그 재연결하는 견고한 스트림 루프입니다.
        """
        if target_profile is None:
            target_profile = MockTargetProfile()

        print(f"\n🛡️ [Day 132 Anti-Crash] 결함 허용(Fault-Tolerance) 전파 파이프라인 가동")
        print(f" 📡 모니터링 타겟: {target_key.upper()} | 최대 복구 제한: {self.max_retries}회")
        print("-" * 80)
        
        retry_count = 0
        loop_count = 0

        # 💡 [과학적 제한] 최대 500번만 샘플을 수집하고 관측을 아름답게 끝내도록 목표 설정
        max_observation_cycles = 500
        
        while self.is_running and retry_count < self.max_retries:
            try:
                # -----------------------------------------------------------------
                # 1. 하드웨어 데이터 수집 및 단선 시뮬레이션 
                # -----------------------------------------------------------------
                loop_count += 1

                if loop_count >= max_observation_cycles:
                    print(f"\n\n🏁 [OBSERVATION COMPLETE] 계획된 {max_observation_cycles}주기 관측 임무를 무결하게 완수했습니다!")
                    print(f"💾 수집된 텐서 데이터를 FITS 아카이브 엔진으로 전송합니다.")
                    self.is_running = False
                    break # while 루프 탈출
                
                # 💡 [실전 테스트용 트랩] 8번째 루프마다 50% 확률로 순간적 USB 버스 연결 유실 유발
                if loop_count % 200 == 0 and random.random() < 0.05:
                    raise ConnectionError("LibUSB_Error: SDR Hardware Device Disconnected (USB Bus Reset)")
                
                # 정상 수신 상태 알고리즘 가동 (SDR 샘플링 버퍼 가상 로드)
                mock_iq = np.random.normal(0, 1, target_profile.sample_rate // 1000)
                
                # 정상 수신 중일 때는 화면에 스트림 인디케이터 표시
                if loop_count % 2 == 0:
                    print(f" 🟢 [STREAMING] Raw IQ Samples Processing... Buffer Size: {len(mock_iq)} | Status: HEALTHY", end="\r")
                
                # 에러 없이 루프 통과 시 복구 카운터 초기화 (완전 안정 상태)
                retry_count = 0
                time.sleep(0.2) # 파이프라인 수집 주기
                
            except (ConnectionError, AttributeError, RuntimeError) as e:
                # -----------------------------------------------------------------
                # 2. 하드웨어 유실 에러 안전 포획 (Safe Catch & Guardian Detector)
                # -----------------------------------------------------------------
                print("\n" + "=" * 80)
                retry_count += 1
                
                # 📌 [핵심] 수학적 지수 백오프 타임 아웃 유도 (2^1=2s, 2^2=4s, 2^3=8s, 2^4=16s...)
                wait_time = 2 ** retry_count
                
                print(f"🚨 [HARDWARE CRITICAL] RTL-SDR 안테나 하드웨어 연결 유실 기습 감지!!")
                print(f"  🔹 에러 원인: {e}")
                print(f"  🔄 시스템 크래시를 차단합니다. {wait_time}초 대기 후 핫플러그(Hot-Plug) 복원 회로를 가동합니다.")
                print(f"  📊 복구 시도 링 오퍼레이션: ({retry_count} / {self.max_retries})")
                print("-" * 80)
                
                # 메인 쓰레드가 죽지 않도록 리소스를 일시 동결(Hold)하고 지수 시간만큼 대기
                time.sleep(wait_time)
                
                # -----------------------------------------------------------------
                # 3. 하드웨어 레지스터 초기화 및 버스 재탐색 (Self-Healing Core)
                # -----------------------------------------------------------------
                print(f"⚡ [하드웨어 자동 복구 시도] RTL-SDR Blog V4 레지스터 초기화 및 USB 포트 락인 중...")
                
                # 가상 드라이버 재부팅 확률 시뮬레이션 (2회 차 시도부터 복구 성공률 90% 세팅)
                if retry_count >= 1 and random.random() < 0.9:
                    print(f"✅ [복구 완료] 하드웨어 버스 핫플러그 재전성 성공!")
                    print(f" 📡 관측 중심 주파수: {target_profile.center_freq/1e6:.4f} MHz로 파이프라인 원격 복귀 완료.")
                    print("=" * 80)
                    # 복구 성공했으므로 루프 카운트를 조절하여 스트림 흐름 재기동
                    loop_count = 0
                else:
                    print(f"❌ [복구 실패] 하드웨어 레이어가 아직 무응답(Dead) 상태입니다. 다음 백오프 시퀀스로 진입합니다.")
                    print("=" * 80)
                    
        if retry_count >= self.max_retries:
            print(f"\n🛑 [SYSTEM HALT] 지정된 {self.max_retries}회의 재연결 시도가 전부 실패했습니다.")
            print(f"⚠️  원인: 안테나 케이블 완전 이탈 또는 전력 차단. 시스템을 안전하게 다운(Graceful Shutdown)합니다.")
            self.is_running = False

if __name__ == "__main__":
    pipeline = ResilientSignalPipeline()
    # 파이프라인 생존성 스트림 가동
    pipeline.start_resilient_stream(target_key="milkyway")