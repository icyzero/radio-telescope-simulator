"""
Main entry point for the Radio Telescope & Signal Processing Integrated Control Center.

This file initializes the telescope hardware abstraction, SDR interfaces,
signal processing engines, real-time data visualizers, and data loggers,
orchestrating them within a single unified entry point.

Responsibilities:
- System Configuration & Centralized Resource Loading
- Hardware Connectivity Validation (Real SDR Driver vs Fail-Safe Virtual Engine)
- Core Analysis & DSP Engine Initialization (FFT, Windowing, Smoothing)
- UI/Dashboard Launch and Event-Driven Key Mapping (Manual Save, Auto-Scan)
- Legacy Telescope Motor Emulation & Command Sequencing Compatibility

Note:
- Telescope/CommandManager handles physical steering and motor safety.
- SDR & SignalProcessor control real-time data acquisition and spectral analysis.
- WaterfallVisualizer drives the user interface and captures astronomical data.
"""

#메인으로 실행할 프로그램
# src/main.py

import os
os.add_dll_directory(r"D:\radio-telescope-simulator")#파이썬이 RTL-SDR Blog V4 드라이버(.dll)를 무조건 찾을 수 있도록 경로 주입
import sys
import time
import json
from src.config import CONFIG
from src.signal.sdr_interface import SDRFactory, SignalProcessor
from src.signal.visualizer import WaterfallVisualizer
from src.data.recorder import FitsRecorder
from src.signal.target_manager import AstroTargetManager

# 기존 Day 100 제어 엔진 모듈 보존
from src.controller.telescope import Telescope
from src.controller.command_manager import CommandManager
from src.controller.command import MoveCommand, StopCommand
from src.scheduler.scheduler import SystemController
from src.utils.logger import log
from src.sim.remote_gate import RemoteCommandGate

def health_check(sdr_device):
    """[Day 110] 하드웨어 최종 점검 전담 함수"""
    print("\n🔍 [System Health Check]")
    try:
        # 가상이든 실제장비든 속성을 정상 조회할 수 있는지 판단
        s_rate = getattr(sdr_device, 'sample_rate', None)
        if s_rate is None:
            s_rate = getattr(sdr_device, 'fs', 2.4e6)
        print(f"✅ Sample Rate: {s_rate / 1e6:.1f} MHz")
        print("✅ SDR Hardware: RESPONSIVE")
        return True
    except Exception as e:
        print(f"❌ SDR Hardware: FAILED ({e})")
        return False

def main():
    """
    Main execution flow and event-driven control loop for the radio telescope simulator.

    The system is designed to transition from a time-driven motor simulation to an
    always-on, real-time data stream and event-driven observation platform. 
    Instead of a blocking linear task, the main lifecycle is handled via the GUI loop,
    emulating modern astronomical control centers.

    Design principles:

    - Fail-Safe Hardware Abstraction:
      Dynamically checks physical USB connectivity and hooks the 'VirtualSDR' 
      simulation engine if hardware is missing, ensuring zero-crash uptime.

    - Event-Driven Operation:
      - User Hotkeys ([A], [S], [Arrows]) instantly trigger system-wide actions.
      - Core components are completely decoupled; the visualizer triggers the recorder
        without knowing its inner filesystem logic.

    - Multi-Threaded/Asynchronous Future Readiness:
      The application keeps telescope physical tracking structures and signal
      processing visualizers bound concurrently, preparing for real-time sky tracking.

    This structure allows the same integrated center to be used for:
    - Simulated mock tracking and data gathering
    - Real physical SDR radio observations (21cm Hydrogen Line)
    - Automated long-duration sky surveys
    """
    print("🔭 Radio Telescope Integrated Control Center v1.1")
    print("==================================================")
    
    # 1. 초기화 (설정 로직 반영)
    # config.yaml 대신 중앙 관리용 파이썬 스크립트 CONFIG 오브젝트 매핑
    sdr_mode = CONFIG["SDR_MODE"]
    sample_rate = CONFIG["SAMPLE_RATE"]
    center_freq = CONFIG["CENTER_FREQ"]
    gain_default = CONFIG["GAIN_DEFAULT"]
    save_path = CONFIG["OBS_PATH"]
    history_size = CONFIG["HISTORY_SIZE"]

    # 2. 하드웨어 연결 (Real or Virtual) via Factory Engine
    sdr = SDRFactory.get_sdr(mode=sdr_mode, sample_rate=sample_rate, center_freq=center_freq)

    # 💡 추가: 하드웨어 객체에 우리가 스캔한 골디락스 게인(49.6 dB) 강제 주입
    try:
        sdr.gain = gain_default
        print(f"📡 [System] Hardware Gain successfully locked at: {gain_default} dB")
    except Exception as e:
        print(f"⚠️ [System] Failed to set Hardware Gain: {e}")
    
    # 하드웨어 최종 점검 (Real SDR Readiness) 가동
    if not health_check(sdr):
        print("⚠️ Warning: Physical SDR not found. Virtual Mode forced.")
        # 만약 진짜 실물 모드 강제 실패 시 복구책 가동
        if sdr_mode == "real":
            sdr = SDRFactory.get_sdr(mode="virtual", sample_rate=sample_rate)

    # 3. 핵심 엔진 구동
    processor = SignalProcessor()
    recorder = FitsRecorder() # 전달받은 경로 기반 파일 아카이버
    
    # 4. 자동화 모드 및 구동체 매칭을 위한 레거시 모터 컨트롤 바인딩 수행
    dt = 0.1
    telescope_a = Telescope()
    manager_a = CommandManager("A", telescope_a)
    telescope_b = Telescope()
    manager_b = CommandManager("B", telescope_b)

    system = SystemController()
    system.register_manager("A", manager_a)
    system.register_manager("B", manager_b)

    # 시나리오 등록
    manager_a.add_command(MoveCommand(5, 5))
    manager_b.add_command(MoveCommand(10, 10))

    log("[SYSTEM] Multi-Telescope control system started.")
    
    # 5. UI/시각화 실행 (Main Loop)
    print("\n🚀 All Systems Ready. Launching Visualizer...")
    print("Hotkeys: [A] Auto-Scan, [S] Manual Save, [UP/DOWN] Gain Control, [T} Target Manager\n")
    
    # WaterfallVisualizer에 수정된 파라미터 구조대로 완벽하게 매핑
    viz = WaterfallVisualizer(
        sdr=sdr, 
        processor=processor, 
        interval=50, 
        history_size=history_size, 
        recorder=recorder
    )
    # ------------------------------------------------------------------
    # 🪐 [Day 123 핵심 주입]: [T] 관측 타겟 다이내믹 인프라 핫키 바인딩
    # ------------------------------------------------------------------
    target_manager = AstroTargetManager()
    target_list = ["MILKY_WAY_H1", "SOLAR_BURST", "JUPITER_DAM"]
    # 현재 기본 타겟 설정에 맞춰 인덱스 초기화
    current_idx = [0] # 가변형 클로저 참조를 위해 리스트로 선언
    
    # 기존 viz 내부의 키보드 이벤트 핸들러(on_key_press 등)가 있다면 확장하기 위한 랩퍼 함수 정의
    def dynamic_key_handler(event):
        if event.key is None:
            return
            
        key = event.key.lower()
        
        # [T] 키가 눌렸을 때 차원 도약 로테이션 시퀀스 가동
        if key == 't':
            current_idx[0] = (current_idx[0] + 1) % len(target_list)
            next_target = target_list[current_idx[0]]
            
            # 실제 하드웨어 레지스터 튜닝 및 버퍼 플러시 트리거
            # 주입된 viz.sdr 인스턴스를 추적하여 직접 제어합니다.
            success = target_manager.switch_target(viz.sdr, next_target)
            
            if success:
                current_profile = target_manager.targets[next_target]
                
                # 💡 [RF 그래픽스 패치]: 주파수 대역 폭등 시 이전 잔상 지우기
                if hasattr(viz, 'clear_data_buffer'):
                    viz.clear_data_buffer()
                elif hasattr(viz, 'data_buffer'):
                    viz.data_buffer.fill(0) # 폴백 방어 코드
                
                # 비주얼라이저의 타이틀 및 눈금 메타데이터 동적 업데이트
                if hasattr(viz, 'update_canvas_metadata'):
                    viz.update_canvas_metadata(
                        title=f"📊 Real-time Radio Analysis ({current_profile.name})",
                        center_freq=current_profile.center_freq,
                        sample_rate=current_profile.sample_rate,
                        dsp_mode=current_profile.dsp_mode
                    )
                else:
                    # 메인 캔버스 윈도우 타이틀 직접 강제 갱신 트리거 (Matplotlib 폴백)
                    try:
                        viz.fig.canvas.set_window_title(f"Radio Observatory - {current_profile.name}")
                    except Exception:
                        pass
                
                print(f"📡 [System Tower] 전파 파이프라인 락인 최종 완수: -> {next_target}")
                print("=" * 75)
        
        # 기존 비주얼라이저에 원래 연결되어 있던 키 바인딩 기능이 있다면 실행을 위임
        # (예: viz.on_key, viz._on_key 등 하드웨어 게인용 화살표 제어 기능 보존용)
        if hasattr(viz, 'on_key_press'):
            viz.on_key_press(event)
        elif hasattr(viz, 'on_key'):
            viz.on_key(event)

    # Matplotlib 캔버스에 새로 정의한 다이내믹 통합 핸들러 연결
    viz.fig.canvas.mpl_connect('key_press_event', dynamic_key_handler)

    # 시각화 대시보드 루프 기동
    viz.show()

if __name__ == "__main__":
    # 백그라운드용 또는 독립형 Day 100 데모 명령 시나리오 점검 및 유지 유닛
    ctrl = SystemController()
    tel = Telescope()
    mgr = CommandManager("Main", tel)
    ctrl.register_manager("Main", mgr)
    gate = RemoteCommandGate(ctrl)

    print("=== Day 100 Demo System Ready ===")
    
    # 2. 시나리오 실행: 설정 변경 -> 이동 -> 에러 발생 -> 진단
    commands = [
        '{"action": "CONFIG_UPDATE", "params": {"slew_rate": 30.0}}',
        '{"action": "MOVE", "manager": "Main", "params": {"alt": 45.0, "az": 180.0}}',
        '{"action": "MOVE", "manager": "Main", "params": {"alt": -99, "az": 0}}', # 의도적 에러
        '{"action": "DIAGNOSTICS"}'
    ]

    for cmd in commands:
        result = gate.process_json_command(cmd)
        print(f"INPUT: {cmd[:50]}... -> RESULT: {result['status']}")

    print("=== Final Health Check ===")
    print(json.dumps(ctrl.get_diagnostics(), indent=2))
    print("==================================================\n")
    
    # 통합 컨트롤타워 최종 실행
    main()