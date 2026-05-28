# src/analysis/validator.py

import numpy as np

class AstroDataValidator:
    def __init__(self):
        pass

    def validate_data(self, target_key, data_matrix):
        """
        수집된 데이터 행렬의 통계적 특성(평균, 편차, 피크 스파이크)을 분석하여
        과학적 관측 데이터로서의 유효성을 등급(Grade)으로 평가합니다.
        """
        print(f"\n🔍 [Day 125 Validator] 실시간 전파 데이터 품질 검사 가동 ➡️ Mode: {target_key}")
        print("-" * 75)
        
        # 💡 데이터 유실 및 빈 배열 예외 방어
        if data_matrix is None or len(data_matrix) == 0:
            return False, "F (Null Data)", "수신된 전파 데이터 프레임이 비어 있습니다."

        # 기본 통계량 추출 (주로 dB 전력 단위 분석)
        mean_val = np.mean(data_matrix)
        max_val = np.max(data_matrix)
        std_val = np.std(data_matrix)
        
        # SNR (신호 대 잡음비) 통계적 추정 알고리즘
        snr = (max_val - mean_val) / (std_val + 1e-6)
        
        grade = "C (Raw Noise)"
        is_valid = True
        reason = "일반적인 배경 우주 무선 노이즈 상태입니다."

        # 1. 은하수 중성수소선 모드 검사
        if target_key == "MILKY_WAY_H1":
            # 수소선 도플러 피크가 통계적 요동 바닥 위로 유의미하게 솟구쳤는지 검사
            if snr > 4.5:
                grade = "A (Excellent Science Data)"
                reason = "도플러 시선 속도 축 상에 명확한 중성 수소선(H-Line) 피크가 검출되었습니다!"
            elif snr > 2.5:
                grade = "B (Good Baseline)"
                reason = "은하수 신호 오프셋이 존재하나 배경 감쇄 보정 처리가 필요합니다."

        # 2. 태양 전파 폭발 모드 검사 (강력한 간헐적 고에너지 임펄스 탐지)
        elif target_key == "SOLAR_BURST":
            # 정상적인 태양 버스트는 기저선 대비 순간 SNR이 6배 이상 튀어야 함
            if max_val > -10.0 and snr > 6.0:
                grade = "A (Solar Burst Detected)"
                reason = "태양 플레어 또는 CME 활동으로 추정되는 초고에너지 전파 폭발 신호가 포착되었습니다!"
            # 지나치게 높은 비정상 전력(앰프가 찢어지는 현상)은 주변 가전제품이나 5G 무선 RFI일 확률이 높음
            elif max_val > 15.0 or snr > 15.0: 
                grade = "F (RFI / Saturation)"
                is_valid = False
                reason = "근접 인공 전파 방해(RFI) 또는 앰프 가포화로 인해 과학적 데이터 가치를 상실했습니다."

        # 3. 목성 단파 모드 검사 (초고속 전압 변조 및 전리층 노이즈 변동 폭 탐지)
        elif target_key == "JUPITER_DAM":
            # 목성 이오 S-버스트는 노이즈 레벨의 변동성(분산 표준편차)이 적정 범위에서 요동침
            if 0.3 < std_val < 3.0:
                if snr > 5.0:
                    grade = "A (Jupiter DAM Candidate)"
                    reason = "목성 이오(Io) 위성 자기장 상호작용 특유의 비열적 싱크로트론 단파 버스트 포착!"
                else:
                    grade = "B (Mild Radio Storm)"
                    reason = "목성 전파 폭풍 기저 신호 감지, 단파대 대역 통과 필터링 권장."
            elif std_val >= 3.0 or max_val > 20.0:
                grade = "F (Severe Atmospheric Noise)"
                is_valid = False
                reason = "지구 전리층 교란 또는 낙뢰성 단파대역 고전력 잡음으로 인해 데이터가 오염되었습니다."

        print(f"📊 [품질 분석 리포트]")
        print(f"   🔹 수신 등급 : {grade}")
        print(f"   🔹 통계 지표 : Peak={max_val:.2f} dB | Std={std_val:.2f} dB | Real-SNR={snr:.2f}")
        print(f"   🔹 판단 사유 : {reason}")
        print("=" * 75)
        
        return is_valid, grade, reason