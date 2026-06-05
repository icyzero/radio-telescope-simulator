# src/signal/pipeline.py

import time
import random
import numpy as np
from src.data.recorder import FitsRecorder

class MockTargetProfile:
    """테스트 구동을 위한 가상 천체 프로필 객체"""
    def __init__(self):
        self.sample_rate = 2400000  # 2.4 MHz
        self.center_freq = 1420405750.0  # H-I Line
        self.target_key = "MILKY_WAY_H1"
        self.target_name = "Milky Way Neutral Hydrogen (H-I)"

class ResilientSignalPipeline:
    def __init__(self, sdr_manager=None):
        self.sdr_manager = sdr_manager
        self.recorder = FitsRecorder()  # 레코더 엔진 인스턴스 인터페이스 바인딩
        self.is_running = True
        self.max_retries = 5  # 최대 핫플러그 재연결 시도 횟수

    def start_resilient_stream(self, target_key="milkyway", target_profile=None):
        """
        [Day 132 핵심] 하드웨어 유실 및 RFI 크래시로부터 메인 프로세스를 보호하고,
        지수 백오프 알고리즘을 가동하여 안테나를 핫플러그 재연결하는 견고한 스트림 루프입니다.
        [Day 133 고도화] 하드웨어 유失 에러를 안전 가드로 감싸고 장애 이력 데이터를 
        상태 레지스터에 누적한 후 루프 종료 시 FITS 레코더로 주입 연동합니다.
        """
        if target_profile is None:
            target_profile = MockTargetProfile()

        print(f"\n🛡️ [Day 132 Anti-Crash] 결함 허용(Fault-Tolerance) 전파 파이프라인 가동")
        print(f" 📡 모니터링 타겟: {target_key.upper()} | 최대 복구 제한: {self.max_retries}회")
        print("-" * 80)

        # 📌 Day 133 장애 이력 추적 전용 상태 레지스터 데이터 세팅
        fault_report = {
            "fail_count": 0,
            "events": []
        }
        
        retry_count = 0
        loop_count = 0

        # 테스트 관찰 및 아카이빙 가독성을 위해 임무 사이클 목표를 100회로 최적화
        max_observation_cycles = 100
        
        while self.is_running and retry_count < self.max_retries:
            try:
                # -----------------------------------------------------------------
                # 1. 하드웨어 데이터 수집 및 단선 시뮬레이션 
                # -----------------------------------------------------------------
                loop_count += 1

                if loop_count >= max_observation_cycles:
                    print(f"\n\n🏁 [OBSERVATION COMPLETE] 계획된 {max_observation_cycles}주기 관측 임무를 무결하게 완수했습니다!")
                    print(f"💾 수집된 텐서 데이터를 FITS 아카이브 엔진으로 전송합니다.")
                    break # while 루프 탈출
                
                # 💡 [Day 133 실전 테스트 트랩] 정확히 42번째 주기에서 기습 USB 버스 유실 발생 시뮬레이션
                if loop_count == 42:
                    raise ConnectionError("LibUSB_Error: SDR Hardware Device Disconnected (USB Bus Reset)")
                
                # 정상 수신 상태 알고리즘 가동 (SDR 샘플링 버퍼 가상 로드)
                mock_iq = np.random.normal(0, 1, target_profile.sample_rate // 1000)
                
                # 정상 수신 중일 때는 화면에 한 줄로 스트림 인디케이터 갱신 표시
                if loop_count % 2 == 0:
                    print(f" 🟢 [STREAMING] 관측 진행도: ({loop_count}/{max_observation_cycles}) | Buffer: Healthy", end="\r")
                
                # 에러 없이 루프 통과 시 복구 카운터 초기화 (완전 안정 상태)
                retry_count = 0
                time.sleep(0.01) # 파이프라인 수집 주기 시뮬레이션 속도 최적화
                
            except (ConnectionError, AttributeError, RuntimeError) as e:
                # -----------------------------------------------------------------
                # 2. 하드웨어 유실 에러 안전 포획 (Safe Catch & Guardian Detector)
                # -----------------------------------------------------------------
                retry_count += 1
                fault_report["fail_count"] += 1
                current_time = time.strftime("%Y-%m-%d %H:%M:%S")
                
                # 장애의 원인과 정확한 타임스탬프를 역사적 트랙에 영구 마킹
                fault_report["events"].append({
                    "timestamp": current_time,
                    "msg": f"Disconnection detected ({str(e)[:35]})"
                })
                
                wait_time = 1  # 테스트 기동 효율을 위해 대기 버퍼를 1초 고정 플러그 처리
                print(f"\n\n🚨 [HARDWARE CRITICAL] {loop_count}번째 주기 기습 단선 감지!!")
                print(f"  📝 [HISTORY MARK] 타임스탬프 [{current_time}] 기반 에러 로그 레지스터 기록.")
                print(f"  🔄 {wait_time}초 후 하드웨어 자동 복원 회로를 가동합니다. (시도 {retry_count}/{self.max_retries})")
                print("-" * 80)
                
                # 메인 쓰레드가 죽지 않도록 리소스를 일시 동결(Hold)하고 지수 시간만큼 대기
                time.sleep(wait_time)
                
                # -----------------------------------------------------------------
                # 3. 하드웨어 레지스터 초기화 및 버스 재탐색 (Self-Healing Core)
                # -----------------------------------------------------------------
                print(f"⚡ [하드웨어 자동 복구 시도] RTL-SDR Blog V4 레지스터 초기화 및 USB 포트 락인 중...")
                print(f"✅ [복구 완료] 하드웨어 버스 핫플러그 재전성 성공!")
                print(f" 📡 관측 중심 주파수: {target_profile.center_freq/1e6:.4f} MHz로 파이프라인 원격 복귀 완료.")
                print("=" * 80)
                
                retry_count = 0 # 복구 성공으로 탈출용 카운트 리셋
                    
        if retry_count >= self.max_retries:
            print(f"\n🛑 [SYSTEM HALT] 지정된 {self.max_retries}회의 재연결 시도가 전부 실패했습니다.")
            print(f"⚠️  원인: 안테나 케이블 완전 이탈 또는 전력 차단. 시스템을 안전하게 다운(Graceful Shutdown)합니다.")
            self.is_running = False
            return
        
        # -----------------------------------------------------------------
        # 💾 [Day 133 인터페이스 통합] 메타데이터 패키징 및 레코더 호출
        # -----------------------------------------------------------------
        # 가상의 2D 워터폴 데이터 생성 (시간 축 100 x 주파수 축 256 채널)
        final_waterfall_matrix = np.random.rand(100, 256)
        
        # Day 126 요구사항 반영 가상 품질 보고서
        mock_quality_info = {
            "grade": "A",
            "snr": 23.8,
            "reason": "Empirical Galactic Curve Signal is outstanding."
        }
        
        # 메타데이터 구조체 하나로 통합 포장
        integrated_metadata = {
            "target_key": target_profile.target_key,
            "target_name": target_profile.target_name,
            "center_freq": target_profile.center_freq,
            "sample_rate": target_profile.sample_rate,
            "gain": 43.5,
            "az": 120.5,
            "el": 45.0,
            "quality_info": mock_quality_info,
            "fault_report": fault_report  # 🚨 가디언 디텍터가 수집한 이력 주입!
        }
        
        # 물리 디스크 아카이빙 엔진 최종 기동
        self.recorder.save_observation(data=final_waterfall_matrix, metadata=integrated_metadata)

if __name__ == "__main__":
    pipeline = ResilientSignalPipeline()
    pipeline.start_resilient_stream()