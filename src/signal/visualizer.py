# src/signal/visualizer.py

import numpy as np
import matplotlib.pyplot as plt
import threading
from matplotlib.animation import FuncAnimation
from src.data.recorder import FitsRecorder

OBS_PLAN = [
    {"freq": 1420.4e6, "duration": 5, "label": "ON_Target_H1"},
    {"freq": 1425.0e6, "duration": 5, "label": "OFF_Background"}
]

class SpectrumVisualizer:
    def __init__(self, sdr, processor, interval=50): # 갱신 속도를 50ms로 높여 더 부드럽게 설정
        self.sdr = sdr
        self.processor = processor
        self.interval = interval
        self.history = None
        
        # 1. 그래프 디자인 (다크 모드 스타일로 전파 관측 느낌 강조)
        plt.style.use('dark_background')
        self.fig, self.ax = plt.subplots(figsize=(12, 6))
        self.line, = self.ax.plot([], [], lw=1.5, color='#33ff33') # 네온 그린
        
        # 2. 물리적 축 설정 (SDR 사양 반영)
        self.fs = getattr(sdr, 'sample_rate', getattr(sdr, 'fs', 2.4e6)) # 변경 코드: 실제 SDR(sample_rate)과 가상 SDR(fs) 모두 지원하도록 수정
        
        # 💡 [Day 117] 단독 스펙트럼 뷰어도 도플러 속도 축 사전 연산 주입
        self.c = 299792.458
        self.f_rest = 1420.40575e6
        c_freq = getattr(sdr, 'center_freq', 1420.4e6)
        
        freq_offsets = np.fft.fftshift(np.fft.fftfreq(2048, 1.0 / self.fs))
        absolute_freqs = c_freq + freq_offsets
        self.velocities = self.c * (1.0 - (absolute_freqs / self.f_rest))
        
        # 💡 물리적 가로축 경계를 속도 대역으로 락(Lock)
        self.ax.set_xlim(self.velocities[0], self.velocities[-1]) 
        self.ax.set_ylim(-50, 70) # 로그 스케일이므로 음수 대역까지 표현
        self.ax.set_xlabel("Line-of-Sight Velocity (km/s)", fontsize=12) # 레이블 수정
        self.ax.set_ylabel("Power Density (dB)", fontsize=12)
        self.ax.set_title("🌌 Real-time Radio Spectrum Analyzer (Velocity Profile)", fontsize=15, pad=20)
        self.ax.grid(True, color='gray', linestyle='--', alpha=0.3)

    def init_plot(self):
        self.line.set_data([], [])
        return self.line,

    def update(self, frame):
        # [Day 101 로직 연동]
        samples = self.sdr.read_samples(2048)
        psd = self.processor.get_power_spectrum(samples)
        
        # [핵심] 로그 스케일 변환: 1,000,000배 차이를 60dB 차이로 압축
        db_psd = 10 * np.log10(psd + 1e-12)
        
        self.line.set_data(self.velocities, db_psd)
        return self.line,

    def show(self):
        self.ani = FuncAnimation(self.fig, self.update, init_func=self.init_plot,
                                 interval=self.interval, blit=True)
        plt.show()

class WaterfallVisualizer:
    # 💡 수정: 메인 엔진에서 주입하는 FitsRecorder 인스턴스를 직접 받도록 파라미터(recorder) 추가
    def __init__(self, sdr, processor, interval=50, history_size=100, recorder=None):
        self.sdr = sdr
        self.processor = processor
        self.interval = interval
        self.history_size = history_size
        self.fs = getattr(sdr, 'sample_rate', getattr(sdr, 'fs', 2.4e6))  # 실제 SDR(sample_rate)과 가상 SDR(fs) 모두 지원
        num_samples = 2048
        
        # ----------------------------------------------------
        # [Day 117: 천문학 도플러 속도 축 사전 연산 엔진]
        # ----------------------------------------------------
        self.c = 299792.458          # 빛의 속도 (km/s)
        self.f_rest = 1420.40575e6    # 수소선 고유 주파수 (Hz)
        
        # 하드웨어 설정 주파수 안전하게 로드 (기본값 1420.4 MHz)
        c_freq = getattr(sdr, 'center_freq', 1420.4e6)
        
        # FFT 빈 주파수 그리드 생성
        freq_offsets = np.fft.fftshift(np.fft.fftfreq(num_samples, 1.0 / self.fs))
        absolute_freqs = c_freq + freq_offsets
        
        # 도플러 공식 역산: 주파수가 높으면 다가옴(-), 낮으면 멀어짐(+)
        self.velocities = self.c * (1.0 - (absolute_freqs / self.f_rest))
        
        # 맷플롯립 Extent 맵핑을 위한 속도 양 끝점 산출 (약 -251.8 ~ 254.5 km/s)
        v_min, v_max = self.velocities[0], self.velocities[-1]
        # ----------------------------------------------------
        
        plt.style.use('dark_background')
        # 1. 2단 레이아웃 설정
        self.fig, (self.ax_spec, self.ax_water) = plt.subplots(2, 1, figsize=(9, 7), sharex=True)

        # 외부 주입 리코더 안전장치
        self.recorder = recorder if recorder is not None else FitsRecorder()
        self.fig.canvas.mpl_connect('key_press_event', self.on_key)
        
        # 2. 상단: Spectrum Line
        self.line, = self.ax_spec.plot([], [], lw=1, color='#00ff00')
        self.ax_spec.set_ylim(-50, 70)
        self.ax_spec.set_xlim(v_min, v_max) # 💡 추가: 상단 차트 가로축 범위를 우주 속도로 락(Lock)
        self.ax_spec.set_ylabel("Power (dB)")
        self.ax_spec.set_title("🌌 Real-time Radio Analysis (Milky Way Velocity Profile)")

        # 3. 하단: Waterfall Image
        # 2D 버퍼 초기화 (시간 x 주파수)
        self.waterfall_buffer = np.full((self.history_size, num_samples), -50.0)
        
        # 💡 수정: extent의 가로축 범위를 [주파수]에서 [우주 속도 v_min, v_max]로 완벽 전환!
        self.img = self.ax_water.imshow(
            self.waterfall_buffer, 
            aspect='auto', 
            cmap='magma', 
            vmin=-30, vmax=50,
            extent=[v_min, v_max, self.history_size, 0] # 💡 주파수 오프셋 대신 속도 도메인 매핑
        )
        self.ax_water.set_xlabel("Line-of-Sight Velocity (km/s)") # 💡 레이블 업데이트
        self.ax_water.set_ylabel("Time History (Frames)")

        # 💡 [Day 117 패치]: 마우스 커서가 차트 위에 올라갈 때 AttributeError로 터지는 버그 완벽 방어
        self.img.format_cursor_data = lambda data: "" 
        self.ax_spec.format_cursor_data = lambda data: ""

    def on_key(self, event):
        # 1. [S] 키: 수동 파일 저장
        if event.key == 's' or event.key == 'S':
            self.recorder.save_observation(self.waterfall_buffer, {"az": 0, "el": 0})
            print("💾 관측 데이터가 FITS 파일로 기록되었습니다.")
        
        # 2. [UP / DOWN] 방향키: 하드웨어 유효 게인 스텝 제어 (v1.1 최종 직결 패치)
        elif event.key == 'up' or event.key == 'down':
            # 💡 로그 분석으로 판명된 RTL-SDR 하드웨어 고유의 실제 유효 dB 스텝 (총 6단계)
            valid_gains = [0.0, 8.7, 14.4, 28.0, 37.2, 49.6]
            
            # 현재 SDR의 실제 하드웨어 게인 값 동기화 (기본값은 최하단)
            current_gain = getattr(self.sdr, 'gain', 0.0)
            
            # 💡 만약 드라이버가 10배 정수형(예: 496)으로 값을 뱉는 체계라면 소수점 스케일로 보정
            if current_gain > 50.0:
                current_gain = current_gain / 10.0
                
            # 가장 가까운 실제 하드웨어 인덱스 매핑
            idx = min(range(len(valid_gains)), key=lambda i: abs(valid_gains[i] - current_gain))
            
            # 방향키에 따라 딱 존재하는 6단계 안에서만 변동
            if event.key == 'up':
                if idx < len(valid_gains) - 1:
                    idx += 1
                direction = "🔊 Gain Up"
            else: # down
                if idx > 0:
                    idx -= 1
                direction = "🔉 Gain Down"
                
            target_gain = valid_gains[idx]
            
            # 하드웨어 주입 (일부 드라이버의 10배 정수형 요구 조건 방어 코드 포함)
            try:
                # 드라이버 특성에 맞춰 target_gain을 그대로 주입해보고, 
                # 만약 드라이버가 내부적으로 10배 형태를 원하면 주입 방식을 자동 분기 처리합니다.
                if hasattr(self.sdr, 'set_gain'):
                    try:
                        self.sdr.set_gain(target_gain)
                    except Exception:
                        self.sdr.set_gain(int(target_gain * 10))
                else:
                    try:
                        self.sdr.gain = target_gain
                    except Exception:
                        self.sdr.gain = int(target_gain * 10)
                        
                # 최종 적용 상태 실시간 동기화 확인 출력
                actual_sdr_gain = getattr(self.sdr, 'gain', target_gain)
                if actual_sdr_gain > 50.0: 
                    actual_sdr_gain = actual_sdr_gain / 10.0
                    
                print(f"{direction}: {actual_sdr_gain:.1f} dB | 정밀 매핑 단계: {idx + 1}/{len(valid_gains)}")
            except Exception as e:
                print(f"⚠️ 게인 설정 동기화 실패: {e}")

        # 3. [A] 키: 자동 관측 시퀀스 가동
        elif event.key == 'a' or event.key == 'A':
            if not hasattr(self, 'scheduler'):
                from src.scheduler.scheduler import ObservationScheduler
                self.scheduler = ObservationScheduler(self.sdr, self)
            
            print("\n🚀 [AUTO MODE] 관측 시퀀스를 실행합니다...")
            self.scheduler.start_auto_scan(OBS_PLAN)

    def update(self, frame):
        samples = self.sdr.read_samples(2048)
        raw_psd = self.processor.get_power_spectrum(samples)
        
        # [Day 103 신기능] 신호 평활화 적용
        psd = self.processor.smooth_spectrum(raw_psd, alpha=0.15)
        db_psd = 10 * np.log10(psd + 1e-12)

        # 💡 [Day 117 패치]: 주파수 도약 시 하드웨어 유입 NaN/Infinite 쓰레기 데이터 실시간 필터링
        db_psd = np.nan_to_num(db_psd, nan=-50.0, posinf=50.0, neginf=-50.0)
        
        # 상단 그래프 업데이트
        self.line.set_data(self.velocities, db_psd) #상단 실시간 그래프 가로축에 주파수(freqs) 대신 사전 연산된 속도 축 주입
        
        # 하단 Waterfall 업데이트: 데이터를 위로 한 칸씩 밀고 맨 아래에 새 데이터 삽입
        self.waterfall_buffer = np.roll(self.waterfall_buffer, -1, axis=0)
        self.waterfall_buffer[-1, :] = db_psd
        self.img.set_array(self.waterfall_buffer)
        
        return self.line, self.img

    def show(self):
        # 💡 수정: cache_frame_data=False를 명시하여 무한 캐싱으로 인한 사용자 경고 제거
        self.ani = FuncAnimation(self.fig, self.update, interval=self.interval, blit=True, cache_frame_data=False)
        plt.tight_layout()
        plt.show()