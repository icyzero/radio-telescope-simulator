from src.signal.sdr_interface import VirtualSDR, SignalProcessor
from src.signal.visualizer import SpectrumVisualizer

if __name__ == "__main__":
    # 2.4MHz 샘플링 레이트 (RTL-SDR 표준)
    sdr = VirtualSDR(sample_rate=2.4e6) 
    proc = SignalProcessor()
    
    viz = SpectrumVisualizer(sdr, proc)
    print("🚀 실시간 스펙트럼 분석기를 시작합니다...")
    viz.show()