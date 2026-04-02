#src/sim/archive_dashboard.py

import os
from pathlib import Path
from src.sim.session_reporter import SessionReporter
from src.sim.session_inspector import SessionInspector

class ArchiveDashboard:
    def __init__(self, storage_path="storage"):
        self.storage_path = Path(storage_path)
        self.reporter = SessionReporter(base_path=self.storage_path)
        self.inspector = SessionInspector(storage_path=self.storage_path)

    def render(self):
        """대시보드 전체 화면을 문자열로 반환"""
        stats = self.reporter.generate_global_stats()
        sessions = self.reporter.get_all_sessions()
        
        output = []
        output.append("="*50)
        output.append("🔭 RADIO TELESCOPE SIMULATOR - DASHBOARD")
        output.append("="*50)
        
        # [STATISTICS] 섹션
        output.append("\n[STATISTICS]")
        output.append(f"- Total Sessions : {stats['total_sessions']}")
        output.append(f"- Success Rate   : {stats['success_rate']:.1f}% ({stats['success_count']}/{stats['total_sessions']})")
        
        # [RECENT FAILURES] 섹션
        output.append("\n[RECENT FAILURES]")
        failures = [s for s in sessions if s.get("status") == "FAILED"]
        for i, fail in enumerate(failures[:5], 1): # 최근 5개만 표시
            summary = self.inspector.get_error_summary(fail["session_id"])
            output.append(f"{i}. {fail['session_id']} : [ERROR] {summary['reason']} (at {summary['last_sim_time']}s)")
            
        output.append("\n" + "="*50)
        return "\n".join(output)

    def run_loop(self):
        """사용자 입력을 처리하는 메인 루프"""
        while True:
            # 1. 화면 초기화 (터미널 깨끗하게)
            os.system('cls' if os.name == 'nt' else 'clear')
            
            # 2. 대시보드 출력
            print(self.render())
            
            # 3. 메뉴 출력 및 입력 받기
            print("\n[ACTIONS]")
            print("(1) Inspect Specific Session")
            print("(2) Run Replay (Advanced)")
            print("(3) Exit")
            
            choice = input("\nSelect Action > ").strip()

            if choice == "1":
                self._handle_inspect()
            elif choice == "2":
                print("\n[System] Replay mode is being prepared...")
                input("Press Enter to return...")
            elif choice == "3":
                print("Exiting Dashboard...")
                break
            else:
                print("Invalid choice. Try again.")
                import time
                time.sleep(1)

    def _handle_inspect(self):
        session_id = input("Enter Session ID to inspect: ").strip()
        # 우리가 만든 Inspector의 타임라인 출력 기능 호출
        self.inspector.print_timeline(session_id)
        input("\nPress Enter to return to Dashboard...")