# src/analysis/volume_visualizer.py

import os
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

class Galactic3DVisualizer:
    def __init__(self):
        self.R0 = 8.5  # 태양계에서 은하 중심(Sgr A*)까지의 거리 (kpc)
        self.V0 = 220.0  # 태양계의 은하 중심 기준 공전 속도 (km/s) - kinematic distance 계산에 필요

    def _estimate_distance_kpc(self, v_lsr, l_rad):
        """Kinematic Distance: 평탄한 회전 곡선(V(R)=V0) 가정 하에 시선속도 v_lsr로부터
        은하중심 반경 R을 구하고, 거기서 태양 기준 시선거리 d를 역산합니다.
        R = R0*V0*sin(l) / (v_lsr + V0*sin(l))
        d = R0*cos(l) ± sqrt(R^2 - R0^2*sin^2(l))

        주의(Kinematic Distance Ambiguity): 1/4사분면(내부 은하 방향)에서는 같은 v_lsr에 대해
        근거리/원거리 두 해가 모두 유효합니다. HI 자체흡수 등 추가 정보 없이는 구분할 수 없어,
        여기서는 근거리(near) 해를 기본으로 채택합니다 - 이것도 확정된 답이 아니라 명시적 가정입니다.
        기하학적으로 유효한 해가 없으면 None을 반환합니다.
        """
        sin_l = np.sin(l_rad)
        cos_l = np.cos(l_rad)

        denom = v_lsr + self.V0 * sin_l
        if abs(denom) < 1e-6:
            return None  # 특이점 근처 (분모가 0에 가까움) - 이 방법으로 거리 계산 불가

        R = self.R0 * self.V0 * sin_l / denom
        if R < 0:
            return None  # 물리적으로 불가능한 반경

        discriminant = R**2 - (self.R0 * sin_l)**2
        if discriminant < 0:
            return None  # 실근 없음 - 이 시선 방향에서 기하학적으로 도달 불가능한 R

        sqrt_term = np.sqrt(discriminant)
        d_near = self.R0 * cos_l - sqrt_term
        d_far = self.R0 * cos_l + sqrt_term

        # 근거리/원거리 축퇴: 추가 정보 없이는 근거리를 기본 채택 (명시적 가정)
        d = d_near if d_near > 0 else d_far
        return d if d > 0 else None

    def render_galactic_volume(self, calibrated_arms, longitude_deg=30.0):
        """
        [Day 138 핵심] 도플러 속도 축 데이터를 은하 삼각 측량 공식으로 변환하여
        우리 은하 나선팔의 3차원 공간적 입체 위치와 가스 밀도를 가시화합니다.
        """
        print(f"\n🌌 [Day 138 Visualizer] 우리 은하 3차원 나선팔 구조 입체 투영 시작")
        print(f" 🎯 분석 타겟 은경(Longitude): {longitude_deg}°")
        print("-" * 80)

        # 삼각 함수 연산을 위한 라디안 변환
        l_rad = np.radians(longitude_deg)
        
        X_coords = []
        Y_coords = []
        Z_densities = []
        bubble_sizes = []

        # 태양계 관측소 고정 위치 공식 적용: (0, R_0, 0) -> (0.0, 8.5)
        sun_x, sun_y = 0.0, self.R0

        for idx, arm in enumerate(calibrated_arms):
            v_lsr = arm["velocity_kms"]
            power = arm["power_db"]
            
            # ----------------------------------------------------
            # 📐 [물리학적 기하학 역산: 시선 속도 기반 거리 d(kpc) 추정]
            # ----------------------------------------------------
            d = self._estimate_distance_kpc(v_lsr, l_rad)
            if d is None:
                print(f" ⚠️ [Arm #{idx+1}] 이 시선속도({v_lsr:+.1f} km/s)로는 거리를 역산할 수 없어 건너뜁니다.")
                print("-" * 60)
                continue
                
            # 삼각 변환 공식을 통한 은하 중심 코어(0, 0) 기준 직교 좌표 도출
            # X = d * cos(b) * sin(l), Y = R0 - d * cos(b) * cos(l) (은위 b=0 상정)
            x = d * np.sin(l_rad)
            y = self.R0 - d * np.cos(l_rad)
            
            # 수소 가스 신호 강도(dB)를 3차원 Z축 오프셋 및 물리 밀도 가중치로 치환
            density = np.abs(power)
            
            X_coords.append(x)
            Y_coords.append(y)
            Z_densities.append(density)
            bubble_sizes.append(density * 25)  # 시각적 가시성을 위한 버블 스케일링

            print(f" 🔹 [Arm #{idx+1} 3D 공간 매핑]")
            print(f"    속도: {v_lsr:+.1f} km/s ➡️ 추정 거리 d: {d:.1f} kpc")
            print(f"    투영 좌표: X={x:.2f} kpc, Y={y:.2f} kpc, Z(Density)={density:.2f} dB")
            print("-" * 60)

        # 🎨 Matplotlib 3D 렌더링 캔버스 엔진 가동
        plt.style.use('dark_background')
        fig = plt.figure(figsize=(12, 8))
        ax = fig.add_subplot(111, projection='3d')

        # 1. 은하 중심 코어 (Sgr A* 블랙홀 원점 (0,0,0)) 마킹
        ax.scatter([0], [0], [0], color='yellow', s=300, marker='*', label='Galactic Center (Sgr A*)', zorder=10)
        
        # 2. 태양계 SDR 관측소 위치 (0, 8.5, 0) 마킹
        ax.scatter([sun_x], [sun_y], [0], color='lime', s=150, marker='o', label='Our Solar System (SDR Station)')

        # 3. 직접 관측 데이터 기반 수소 가스 나선팔 3D 공간 버블 투영
        sc = ax.scatter(X_coords, Y_coords, Z_densities, c=Z_densities, cmap='plasma', 
                        s=bubble_sizes, alpha=0.8, edgecolors='cyan', linewidths=1.5, label='Observed H-I Gas Clouds')

        # 4. 전파망원경 빔 조사 방향 가이드 라인 (Line of Sight) 점선 렌더링
        max_d = 15.0
        ax.plot([sun_x, max_d * np.sin(l_rad)], [sun_y, self.R0 - max_d * np.cos(l_rad)], [0, 0], 
                color='gray', linestyle='--', alpha=0.5, label=rf'Telescope Beam Path ($l={longitude_deg}^\circ$)')

        # 📊 학술 규격화 및 축 라벨링
        ax.set_title("Volumetric 3D Mapping of Milky Way Spiral Arms", fontsize=14, fontweight='bold', color='cyan', pad=20)
        ax.set_xlabel("Galactic X-Axis (kpc)", fontsize=11, labelpad=10)
        ax.set_ylabel("Galactic Y-Axis (kpc)", fontsize=11, labelpad=10)
        ax.set_zlabel("Signal Power / Density Offset (dB)", fontsize=11, labelpad=10)
        
        # 은하 규모 공간 스케일 범위 제한 설정
        ax.set_xlim(-10, 15)
        ax.set_ylim(-5, 15)
        ax.set_zlim(0, 30)
        
        # 3D 공간을 직관적으로 바라볼 수 있는 최적의 고도 및 방위각 고정
        ax.view_init(elev=25, azim=-45)
        
        ax.legend(loc='upper right', fontsize=10)
        
        # 가스 밀도 컬러바 우측 배치
        fig.colorbar(sc, ax=ax, shrink=0.5, aspect=10, pad=0.1, label='Gas Density Scale (dB)')

        plt.tight_layout()
        
        # 결과물 물리 저장 디렉토리 보증
        os.makedirs("observations/milkyway/stacked", exist_ok=True)
        output_path = "observations/milkyway/stacked/Galactic_3D_Volume_Map.png"
        plt.savefig(output_path, dpi=300)
        
        print(f"✅ 우리 은하 나선팔 3차원 입체 입자 볼륨 맵 저장 완료! ➡️ {output_path}")
        print("=" * 80)
        plt.show()

if __name__ == "__main__":
    from src.analysis.calibrator import AstroDopplerCalibrator

    visualizer = Galactic3DVisualizer()
    calibrator = AstroDopplerCalibrator()

    master_fits_path = "observations/milkyway/stacked/Master_Stacked_Science_Data.fits"
    real_arms_data = calibrator.calibrate_master_spectrum(master_fits_path)

    if real_arms_data:
        visualizer.render_galactic_volume(real_arms_data, longitude_deg=30.0)
    else:
        print("[Visualizer] 캘리브레이션된 피크가 없어 3D 볼륨을 렌더링할 수 없습니다.")