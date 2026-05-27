# src/signal/target_manager.py

import os
import time

class ObservationTarget:
    def __init__(self, name, center_freq, sample_rate, dsp_mode, description):
        self.name = name
        self.center_freq = center_freq  # Hz
        self.sample_rate = sample_rate  # Hz
        self.dsp_mode = dsp_mode        # DSP 처리 방식 식별자
        self.description = description

class AstroTargetManager:
    def __init__(self):
        # 🪐 전파 천문 관측 멀티 타겟 데이터베이스 정밀 정의
        self.targets = {
            "MILKY_WAY_H1": ObservationTarget(
                name="Milky Way Neutral Hydrogen (H-I)",
                center_freq=1420.40575e6,
                sample_rate=2.4e6,
                dsp_mode="SPECTRUM_AVERAGE",
                description="우리 은하 나선팔의 중성 수소 가스 분포 및 도플러 시선 속도 계산 모드"
            ),
            "SOLAR_BURST": ObservationTarget(
                name="Solar Radio Burst (Type III/IV)",
                center_freq=245.0e6,
                sample_rate=1.0e6,
                dsp_mode="DYNAMIC_WATERFALL",
                description="태양 플레어 활동 및 코로나 질량 방출(CME)로 인한 고에너지 전파 폭발 모니터링 모드"
            ),
            "JUPITER_DAM": ObservationTarget(
                name="Jupiter Decametric Emission (DAM)",
                center_freq=22.2e6,
                sample_rate=0.25e6,
                dsp_mode="FAST_TIME_SERIES",
                description="목성 이오(Io) 위성과의 상호작용으로 발생하는 강력한 비열적 싱크로트론 단파 전파 관측 모드"
            )
        }
        self.current_target = "MILKY_WAY_H1"

    def switch_target(self, sdr, target_key):
        """실물 SDR 하드웨어가 연결되어 있을 때 타겟 프로필에 맞춰 하드웨어 레지스터 동적 변환"""
        if target_key not in self.targets:
            print(f"⚠️ [Target Manager] 존재하지 않는 관측 타겟 키입니다: {target_key}")
            return False
            
        target = self.targets[target_key]
        self.current_target = target_key
        
        print(f"\n🔄 [Target Manager] 관측 모드 동적 스위칭 결정 ➡️ {target.name}")
        print(f" 📜 관측 미션: {target.description}")
        print("-" * 75)
        
        # 실제 하드웨어 제어 인스턴스가 주입되었을 때 레지스터 주입 시작
        if sdr and (hasattr(sdr, 'center_freq') or hasattr(sdr, 'set_center_freq')):
            try:
                # 💡 [RF 엔지니어링 패치]: 내부 필터 붕괴를 막기 위해 Sample Rate 및 Bandwidth 선제 변경
                if hasattr(sdr, 'set_sample_rate'):
                    sdr.set_sample_rate(target.sample_rate)
                else:
                    sdr.sample_rate = target.sample_rate
                
                # 가변 대역폭 옵션이 드라이버단에 존재할 경우 샘플레이트와 1:1 동기화
                if hasattr(sdr, 'set_bandwidth'):
                    sdr.set_bandwidth(target.sample_rate)
                elif hasattr(sdr, 'bandwidth'):
                    sdr.bandwidth = target.sample_rate
                
                # 💡 주파수 잠금(PLL Lock) 최종 실행
                if hasattr(sdr, 'set_center_freq'):
                    sdr.set_center_freq(target.center_freq)
                else:
                    sdr.center_freq = target.center_freq
                
                # 💡 [SDR Blog V4 안전 패치]: 주파수 도약 후 버퍼에 잔류하는 가짜 데이터(Ghost Frame) 강제 플러시
                if hasattr(sdr, 'read_samples'):
                    for _ in range(3):  # 이전 주파수의 찌꺼기 버퍼 프레임 3개 소거
                        sdr.read_samples(1024)
                
                print(f"✅ [하드웨어 락인 성공] 중심 주파수: {target.center_freq/1e6:.3f} MHz | 대역폭: {target.sample_rate/1e6:.3f} MHz")
                print(f"⚙️ [DSP 엔진 동기화] 활성화된 신호 처리 아키텍처: {target.dsp_mode}")
                print("=" * 75)
                return True
                
            except Exception as e:
                print(f"❌ [하드웨어 튜닝 실패] 드라이버 레지스터 주입 중 치명적 오류: {e}")
                print("   💡 이전 관측 주파수 상태를 유지합니다.")
                return False
        else:
            # 실물 하드웨어가 없는 가상 시뮬레이터 환경 대응
            print(f"🤖 [VirtualSDR] 가상 주파수 신호 발생기 프로필 릴리즈 완수")
            print(f" 📍 Virtual Freq ➡️ {target.center_freq/1e6:.3f} MHz | Virtual Rate ➡️ {target.sample_rate/1e6:.3f} MHz")
            print(f" ⚙️ Virtual DSP Pipeline ➡️ {target.dsp_mode} 로드")
            print("=" * 75)
            return True

if __name__ == "__main__":
    # 독립형 아키텍처 인프라 테스트 가동
    manager = AstroTargetManager()
    print("🛰️ 관측 타겟 매니저 인프라 초기화 성공.")
    print("======================================================================")
    
    # 가상 시뮬레이터 환경 프로필 전환 교차 검증
    manager.switch_target(sdr=None, target_key="SOLAR_BURST")
    manager.switch_target(sdr=None, target_key="JUPITER_DAM")