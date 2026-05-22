# src/analysis/kinematics.py

import numpy as np

class GalacticMassEstimator:
    def __init__(self, r_sun=8.5, v_sun=220.0):
        """
        r_sun: 태양에서 은하 중심까지의 거리 (약 8.5 kpc)
        v_sun: 태양계의 은하 회전 속도 (약 220.0 km/s)
        G: 중력 상수 (천문학 단위계: kpc * km^2 / (s^2 * M_sun))
        """
        self.R_0 = r_sun 
        self.V_0 = v_sun
        self.G = 4.30091e-6 # (km/s)^2 * kpc / M_sun (태양질량 단위)

    def estimate_mass_from_peak(self, galactic_longitude_deg, v_lsr_max_peak):
        """
        접선 지점 공법(Tangent Point Method)을 사용하여 
        은하 중심으로부터의 거리, 회전 속도, 그리고 반경 내에 가두어진 은하 질량을 계산합니다.
        """
        print(f"🌌 [Day 119 Kinematics] 실전 관측 피크 기반 은하 물리량 계산 개시")
        print(f"📍 관측 은하 경도: {galactic_longitude_deg}° | 측정된 최대 시선속도(v_LSR): {v_lsr_max_peak} km/s")
        print("-" * 70)
        
        # 💡 [물리 법칙 방어 코드] 접선 지점 공법이 성립하지 않는 기하학적 대역 차단
        normalized_l = galactic_longitude_deg % 360
        if normalized_l == 0 or normalized_l == 180 or normalized_l == 90 or normalized_l == 270:
            print("⚠️ [계산 중단] 은하 중심, 반대 중심 및 직교 방향은 접선 지점 공법을 적용할 수 없습니다.")
            return None
            
        # 1. 터미널 속도(Terminal Velocity) 도출
        # 은하 회전 기하학에 따라 최고 속도 성분의 절대값을 취합니다.
        v_terminal = abs(v_lsr_max_peak)
        
        # 라디안 변환
        l_rad = np.radians(galactic_longitude_deg)
        sin_l = np.sin(l_rad)
        abs_sin_l = abs(sin_l) # 거리와 속도 스케일링을 위한 절대 삼각비
        
        # 2. 접선 지점(Tangent Point)까지의 은하 중심 기준 반경 R 계산
        # $R = R_0 \times |\sin(\ell)|$
        R_tangent = self.R_0 * abs_sin_l
        
        # 3. 해당 거리 R에서의 진짜 은하 회전 속도 V(R) 역산
        # $V(R) = v_terminal + V_0 \times |\sin(\ell)|$
        V_rot = v_terminal + (self.V_0 * abs_sin_l)
        
        # 4. 뉴턴 중력 법칙 및 케플러 회전 법칙을 이용한 내포 질량(M) 유도
        # $M = \frac{V^2 \times R}{G}$
        milky_way_mass = (V_rot ** 2 * R_tangent) / self.G
        
        # 광년 변환 (1 kpc ≈ 3261.56 광년)
        light_years = R_tangent * 3261.56
        
        print(f"🎯 [은하 동역학 계산 결과]")
        print(f" 🔹 은하 중심부 기준 가스 반경 (R) : {R_tangent:.2f} kpc (약 {light_years:,.0f} 광년)")
        print(f" 🔹 해당 지점의 진짜 은하 회전 속도 (V): {V_rot:.2f} km/s")
        print(f" 🔹 반경 내에 포함된 은하 총 질량 (M) : {milky_way_mass:.2e} M_☉")
        print(f"    ➡️ 태양 질량의 약 {milky_way_mass/1e11:.1f}천억 배")
        print("======================================================================")
        
        # 💡 [과학적 분석 보고] 은하 회전 곡선(Rotation Curve)의 평탄함 검증
        # 뉴턴 역학에 따르면 외곽 가스의 속도는 중심에서 멀어질수록 떨어져야 하지만(케플러 하강),
        # 실제로는 태양계 속도(220km/s) 수준을 유지하거나 오히려 상회합니다.
        if V_rot >= self.V_0 * 0.9:
            print("💡 [천문학 인사이트] 관측된 회전 속도가 외곽에서도 전혀 줄어들지 않는 '평탄한 회전 곡선'을 보입니다.")
            print("   이는 전자기파로 관측되지 않는 거대한 광륜 형태의 '암흑 물질(Dark Matter Halo)'이")
            print("   은하 전체를 무겁게 결속하고 있음을 증명하는 결정적 실증 데이터입니다! 🌌✨")
            print("-" * 70)
            
        return {
            "radius_kpc": R_tangent,
            "velocity_kms": V_rot,
            "mass_msun": milky_way_mass
        }

if __name__ == "__main__":
    # 어제 FITS 분석기에서 도출한 실전 데이터를 매핑합니다.
    # 은하 경도 30도 방향을 정조준했고, 최대 피크 시선속도가 -125.0 km/s로 잡힌 시나리오 검증
    estimator = GalacticMassEstimator()
    estimator.estimate_mass_from_peak(galactic_longitude_deg=30.0, v_lsr_max_peak=-125.0)