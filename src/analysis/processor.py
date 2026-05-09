#src/analysis/processor.py
 
import numpy as np
import matplotlib.pyplot as plt

class SignalStraightener:
    def __init__(self, waterfall_data):
        self.data = waterfall_data
        self.rows, self.cols = waterfall_data.shape
        self.center_idx = self.cols // 2

    def de_drift(self, drift_path):
        """
        휘어진 궤적(drift_path)을 따라 각 행을 밀어서 
        신호를 화면 중앙(center_idx)으로 정렬합니다.
        """
        straightened = np.zeros_like(self.data)
        
        for i, peak_pos in enumerate(drift_path):
            # 신호를 중앙으로 보내기 위한 이동량 계산
            shift_amount = self.center_idx - peak_pos
            # np.roll은 배열을 원형으로 회전시켜 데이터를 밀어줍니다.
            straightened[i, :] = np.roll(self.data[i, :], int(shift_amount))
            
        return straightened

    def compare_integration(self, original_data, corrected_data):
        """보정 전과 후의 통합 에너지 비교"""
        # 시간 축(axis=0)으로 에너지를 모두 더함
        integrated_raw = np.sum(original_data, axis=0)
        integrated_corr = np.sum(corrected_data, axis=0)
        
        plt.figure(figsize=(12, 6))
        plt.plot(integrated_raw, label='Raw Integration (Drifted)', alpha=0.7, color='gray')
        plt.plot(integrated_corr, label='De-drifted Integration (Focused)', lw=2, color='#ffcc00')
        
        plt.title("Signal Power Integration: Raw vs De-drifted")
        plt.xlabel("Frequency Bin")
        plt.ylabel("Accumulated Power")
        plt.legend()
        plt.grid(True, alpha=0.2)
        plt.show()