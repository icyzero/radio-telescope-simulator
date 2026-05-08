#src/inspector.py

from src.analysis.inspector import FitsInspector
import os

# 어제 저장한 파일명으로 교체 (실제 파일명 확인 필요)
fits_file = "observations/obs_20260507_211412.fits"

if os.path.exists(fits_file):
    inspector = FitsInspector(fits_file)
    peaks = inspector.analyze_signal()
    inspector.plot_analysis(peaks)
else:
    print(f"파일을 찾을 수 없습니다: {fits_file}")