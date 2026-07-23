# src/scheduler/observation_scheduler.py

import time
import threading
import logging

logging.basicConfig(
    filename='observation_log.txt',
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    encoding='utf-8'
)

"""Day 109 추가"""
class ObservationScheduler:
    def __init__(self, sdr, visualizer):
        self.sdr = sdr
        self.visualizer = visualizer # 현재 waterfall_buffer에 접근하기 위해 필요
        self.is_running = False

    def start_auto_scan(self, plan):
        """별도의 스레드에서 스케줄을 실행하여 UI가 멈추지 않게 합니다."""
        thread = threading.Thread(target=self.run_sequence, args=(plan,))
        thread.start()

    def run_sequence(self, plan):
        self.is_running = True
        msg = f"📅 관측 스케줄 시작: 총 {len(plan)}개 세션"
        print(msg)
        logging.info(msg)

        for i, session in enumerate(plan):
            if not self.is_running: break

            target_mhz = session['freq'] / 1e6
            print(f"\n[Session {i+1}] 🔄 주파수 이동: {target_mhz} MHz")

            self.sdr.center_freq = session['freq']
            time.sleep(1.5)

            print(f"📡 관측 중 ({session['label']}): {session['duration']}초간...")
            time.sleep(session['duration'])

            meta = {
                'label': session['label'],
                'center_freq': session['freq'],
                'duration': session['duration'],
                'az': 180.0,
                'el': 45.0
            }

            try:
                self.visualizer.recorder.save_observation(
                    self.visualizer.waterfall_buffer,
                    meta
                )
                log_msg = f"✅ 저장 완료: {session['label']} ({target_mhz} MHz)"
                print(log_msg)
                logging.info(log_msg)
            except Exception as e:
                err_msg = f"❌ 저장 실패: {e}"
                print(err_msg)
                logging.error(err_msg)

        self.is_running = False
        print("\n🏁 모든 관측 스케줄이 완료되었습니다.")
        logging.info("🏁 All scheduled observations completed.")