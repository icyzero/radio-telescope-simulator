#src/run_dedrift.py

from src.analysis.inspector import FitsInspector
from src.analysis.processor import SignalStraightener

# 1. 어제 저장한 데이터 로드 및 궤적 추출
inspector = FitsInspector('observations/obs_20260507_211412.fits')
drift_path = inspector.analyze_signal()

# 2. Straightener 가동
straightener = SignalStraightener(inspector.data)

# 3. 신호 펴기 (De-drifting)
straightened_data = straightener.de_drift(drift_path)

# 4. 비교 결과 출력
print("🚀 에너지 통합 및 증폭 확인 중...")
straightener.compare_integration(inspector.data, straightened_data)