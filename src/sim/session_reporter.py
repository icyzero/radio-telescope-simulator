# src/sim/session_reporter.py

from pathlib import Path
import json

class SessionReporter:
    def __init__(self, base_path="storage"):
        self.base_path = Path(base_path)

    def get_all_sessions(self):
        """모든 세션 폴더를 탐색하여 메타데이터 리스트 반환"""
        sessions = []
        # session_으로 시작하는 모든 디렉토리 탐색
        for session_dir in self.base_path.glob("session_*"):
            meta_path = session_dir / "session_meta.json"
            if meta_path.exists():
                with open(meta_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    data["session_id"] = session_dir.name
                    sessions.append(data)
        return sessions

    def generate_global_stats(self):
        """전체 세션의 성공률 및 통계 집계"""
        sessions = self.get_all_sessions()
        total = len(sessions)
        success = sum(1 for s in sessions if s.get("status") == "SUCCESS")
        
        return {
            "total_sessions": total,
            "success_count": success,
            "fail_count": total - success,
            "success_rate": (success / total * 100) if total > 0 else 0
        }

    def inspect_session(self, session_id: str):
        log_path = self.base_path / session_id / "events.jsonl"
        if not log_path.exists():
            return None

        # 시간 분석 예시 (Pseudo-logic)
        durations = []
        with open(log_path, "r", encoding="utf-8") as f:
            for line in f:
                event = json.loads(line)
                # 여기서 특정 명령의 시작/끝 시간을 계산하여 저장
                pass
        return durations