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
        
        # 💡 [물리 법칙 방어 코드] Tangent Point 방법론은 1사분면(0°<l<90°)과
        # 4사분면(270°<l<360°)에서만 성립합니다. 그 외 구간(외곽 은하 방향, 90°~270°)은
        # 시선 방향에 '접선 지점' 자체가 존재하지 않아 최대 시선속도가 원운동 속도를
        # 대변하지 못하므로 계산을 차단합니다.
        normalized_l = galactic_longitude_deg % 360
        if normalized_l == 0 or (90 <= normalized_l <= 270):
            print("⚠️ [계산 중단] 접선 지점 공법은 1사분면(0°<l<90°) 또는 4사분면(270°<l<360°)에서만 유효합니다.")
            print(f"   입력된 은경 {galactic_longitude_deg}°는 이 범위를 벗어나 물리적으로 의미 있는 결과를 만들 수 없습니다.")
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
            print(f"💡 [천문학 인사이트] 이 지점(R={R_tangent:.2f} kpc)의 회전 속도가 태양계 수준(220km/s)을 유지하거나 상회합니다.")
            print("   뉴턴 역학의 케플러 하강 예측과는 다른 값으로, 암흑 물질 가설과 일치하는 관측입니다.")
            print("   (단일 지점 관측이므로 이것만으로 은하 전체 회전 곡선의 형태를 단정할 수는 없습니다.)")
            print("-" * 70)
            
        return {
            "radius_kpc": R_tangent,
            "velocity_kms": V_rot,
            "mass_msun": milky_way_mass
        }

if __name__ == "__main__":
    from src.analysis.calibrator import AstroDopplerCalibrator

    estimator = GalacticMassEstimator()
    calibrator = AstroDopplerCalibrator()

    master_fits_path = "observations/milkyway/stacked/Master_Stacked_Science_Data.fits"
    real_peaks = calibrator.calibrate_master_spectrum(master_fits_path)

    if real_peaks:
        # Tangent point 방법론: 이 시선 방향(l)에서 terminal velocity(|v|가 최대인 성분)를 사용
        terminal_peak = max(real_peaks, key=lambda p: abs(p["velocity_kms"]))
        estimator.estimate_mass_from_peak(
            galactic_longitude_deg=30.0,
            v_lsr_max_peak=terminal_peak["velocity_kms"]
        )
    else:
        print("[Kinematics] 캘리브레이션된 피크가 없어 질량을 추정할 수 없습니다.")