# src/analysis/rotation_mapper.py

import os
import numpy as np
import matplotlib.pyplot as plt

class GalacticRotationMapper:
    def __init__(self):
        # IAU(국제천문연맹) 표준 천문 상수 세팅
        self.R0 = 8.5   # 태양계에서 은하 중심까지의 거리 (kpc)
        self.V0 = 220.0 # 태양계의 은하 중심 기준 공전 속도 (km/s)

    def _pick_terminal_velocity_peak(self, calibrated_peaks):
        """Tangent Point 방법론: 하나의 시선 방향(l)에서 관측된 여러 피크 중
        tangent point에 대응하는 것은 그 시선에서 가장 극단적인(|v|가 최대인)
        속도 성분(terminal velocity)입니다."""
        return max(calibrated_peaks, key=lambda p: abs(p["velocity_kms"]))

    def _assess_curve_shape(self, sorted_R, sorted_V):
        """관측점이 충분하고, 가장 바깥쪽 두 점의 속도가 서로 비슷하면 '평평한(flat) 곡선'으로 판단.
        점이 부족하거나 평평하지 않으면 그 사실을 그대로 보고합니다 (고정된 결론 주장 금지)."""
        MIN_POINTS_FOR_SHAPE_CLAIM = 3
        FLATNESS_THRESHOLD = 0.20  # 가장 바깥 두 점의 속도 차이가 이 비율 이내면 "평평하다"고 판단

        n = len(sorted_R)
        if n < MIN_POINTS_FOR_SHAPE_CLAIM:
            return (
                f"Observation Insight:\n"
                f"Only {n} data point(s) available.\n"
                f"Need >= {MIN_POINTS_FOR_SHAPE_CLAIM} points at different\n"
                f"longitudes to assess curve shape."
            )

        v_outer1, v_outer2 = sorted_V[-2], sorted_V[-1]
        relative_diff = abs(v_outer1 - v_outer2) / max(v_outer1, v_outer2, 1e-9)

        if relative_diff <= FLATNESS_THRESHOLD:
            return (
                "Observation Insight:\n"
                "Velocity stays roughly flat at outer radius\n"
                f"(outer two points differ by {relative_diff*100:.1f}%).\n"
                "Consistent with (not proof of) a\n"
                "[Dark Matter Halo] surrounding the Galaxy."
            )
        else:
            return (
                "Observation Insight:\n"
                "Outer-radius velocities are NOT flat\n"
                f"(outer two points differ by {relative_diff*100:.1f}%).\n"
                "Current data does not support a flat-curve claim."
            )

    def generate_rotation_curve(self, observations):
        """
        [재설계] 은경(l)이 서로 다른 여러 관측 결과를 입력받아, 각 관측마다
        terminal velocity 피크 하나로 실제 tangent point (R, V) 좌표를 계산합니다.

        observations: [{"galactic_longitude": float, "calibrated_peaks": [...]}, ...]
        (peaks는 AstroDopplerCalibrator.calibrate_master_spectrum()의 실제 출력 형식)

        주의: tangent point 공식 R = R0*|sin(l)|은 l에만 의존하므로, 같은 l에서 나온
        여러 피크에 각각 다른 R을 부여할 물리적 근거가 없습니다(예전 코드의 배율 항이
        바로 이 문제를 감추려던 시각화용 땜질이었음). 그래서 이 함수는 은경 하나당
        "terminal velocity 피크 1개 -> (R, V) 좌표 1개"만 만듭니다. 여러 점으로 된
        진짜 회전 곡선을 그리려면 서로 다른 은경에서 관측한 데이터가 여러 개 필요합니다.
        """
        print(f"\n[Day 131 Mapper] 우리 은하 회전 곡선 2차원 매핑 시퀀스 개시")
        print(f"입력된 관측 지점 수: {len(observations)}개")
        print("-" * 75)

        distances_kpc = []
        rotation_velocities = []

        for obs in observations:
            l = obs["galactic_longitude"]
            peaks = obs["calibrated_peaks"]
            if not peaks:
                continue

            l_rad = np.radians(l)
            terminal_peak = self._pick_terminal_velocity_peak(peaks)
            v_lsr = terminal_peak["velocity_kms"]

            # 1. 은하 중심으로부터의 물리적 거리 R 유도 (Tangent Point 삼각 측량)
            R = self.R0 * np.abs(np.sin(l_rad))

            # 2. 상대 시선 속도를 은하 중심 기준 공전 속도 V(R)로 변환
            # V(R) = v_lsr + V0 * sin(l)
            V_R = v_lsr + self.V0 * np.sin(l_rad)

            distances_kpc.append(R)
            rotation_velocities.append(np.abs(V_R))

        if not distances_kpc:
            print("⚠️ [경고] 유효한 관측 지점이 하나도 없어 회전 곡선을 그릴 수 없습니다.")
            print("-" * 75)
            return

        # 3. 데이터 포인트 시각화 대시보드 렌더링
        plt.style.use('dark_background')
        plt.figure(figsize=(10, 6))
        
        # 🔴 이론적 케플러 회전 법칙 선 (암흑 물질이 없을 때의 예측선 - 점선)
        r_model = np.linspace(1.5, 18, 100)
        v_kepler = self.V0 * np.sqrt(self.R0 / r_model)
        plt.plot(r_model, v_kepler, '--', color='crimson', alpha=0.7, linewidth=2, 
                 label='Expected Keplerian Decline (No Dark Matter)')
        
        # 🟢 실측 데이터 플로팅 (우리가 하드웨어 스택으로 잡아낸 진짜 은하의 속도)
        plt.scatter(distances_kpc, rotation_velocities, color='cyan', s=160, zorder=5, 
                    edgecolors='white', linewidths=1.5, label='Observed Spiral Arms (Our Telescope)')
        
        # 실측 데이터 경향성 선 연결 (Flat Curve 경향 가시화)
        sorted_idx = np.argsort(distances_kpc)
        plt.plot(np.array(distances_kpc)[sorted_idx], np.array(rotation_velocities)[sorted_idx], 
                 color='cyan', alpha=0.8, linewidth=2.5, linestyle='-')

        # 그래픽 인테리어 및 학술 규격 명명
        plt.title("Empirical Galactic Rotation Curve & Dark Matter Verification", fontsize=13, fontweight='bold', color='lime', pad=15)
        plt.xlabel("Galactocentric Distance $R$ (kpc)", fontsize=11)
        plt.ylabel("Orbital Rotation Velocity $V(R)$ (km/s)", fontsize=11)
        plt.xlim(0, 18)
        plt.ylim(0, 350)
        plt.grid(True, linestyle=':', alpha=0.3, color='gray')
        plt.legend(loc='upper right', fontsize=10)

        # 과학적 해설 주입 박스 (Insight Text Overlay) - 실제 데이터 형태를 판단해서 씀
        sorted_R = np.array(distances_kpc)[sorted_idx]
        sorted_V = np.array(rotation_velocities)[sorted_idx]
        insight_text = self._assess_curve_shape(sorted_R, sorted_V)
        props = dict(boxstyle='round,pad=0.6', facecolor='black', alpha=0.8, edgecolor='cyan')
        plt.gca().text(0.05, 0.08, insight_text, transform=plt.gca().transAxes, fontsize=9.5,
                     verticalalignment='bottom', bbox=props, color='white', fontfamily='monospace')

        plt.tight_layout()
        
        # 이미지 파일 영구 아카이빙
        output_dir = "observations/milkyway/stacked"
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, "Galactic_Rotation_Curve.png")
        
        plt.savefig(output_path, dpi=300)
        print(f"✅ 우리 은하 2차원 회전 곡선 맵 저장 완료!")
        print(f" 📸 그래픽 경로: {output_path}")
        print("=" * 75)
        plt.show()

if __name__ == "__main__":
    from src.analysis.calibrator import AstroDopplerCalibrator

    mapper = GalacticRotationMapper()
    calibrator = AstroDopplerCalibrator()

    master_fits_path = "observations/milkyway/stacked/Master_Stacked_Science_Data.fits"
    real_peaks = calibrator.calibrate_master_spectrum(master_fits_path)

    if real_peaks:
        # 지금 프로젝트엔 이 마스터 스택 하나(=은경 하나)만 존재하므로 관측 지점도 1개.
        # 서로 다른 은경에서 관측한 데이터가 더 생기면 이 리스트에 항목을 추가하면 됨.
        observations = [
            {"galactic_longitude": 30.0, "calibrated_peaks": real_peaks}
        ]
        mapper.generate_rotation_curve(observations)
    else:
        print("[Mapper] 캘리브레이션된 피크가 없어 회전 곡선을 생성할 수 없습니다.")