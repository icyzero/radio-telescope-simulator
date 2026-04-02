# src/sim/session_inspector.py

import json
from pathlib import Path

class SessionInspector:
    def __init__(self, storage_path="storage"):
        self.storage_path = Path(storage_path)

    def get_error_summary(self, session_id: str):
        log_path = self.storage_path / session_id / "events.jsonl"
        if not log_path.exists():
            return {"error": "Log file not found"}

        events = []
        with open(log_path, "r", encoding="utf-8") as f:
            for line in f:
                events.append(json.loads(line))

        # 뒤에서부터 탐색하여 첫 번째 FAILED 이벤트 찾기
        for event in reversed(events):
            if "FAILED" in event["type"] or "ERROR" in event["type"]:
                return {
                    "session_id": session_id,
                    "timestamp": event.get("timestamp"),
                    "error_type": event["type"],
                    "reason": event.get("payload", {}).get("reason", "Unknown"),
                    "last_sim_time": event.get("sim_time")
                }
        return {"status": "No critical errors found"}
    
    # 타임라인 요약 출력 로직
    def print_timeline(self, session_id: str):
        log_path = self.storage_path / session_id / "events.jsonl"
    
        # 🔥 [수정] 파일이 없으면 에러를 내지 않고 정중하게 안내합니다.
        if not log_path.exists():
            print(f"\n[Error] Session '{session_id}'를 찾을 수 없거나 로그 파일이 없습니다.")
            print(f"Path: {log_path}")
            return

        print(f"\n--- [Timeline for {session_id}] ---")
        
        with open(log_path, "r", encoding="utf-8") as f:
            for line in f:
                ev = json.loads(line)
                # 중요 이벤트만 필터링 (시작, 실패, 중단 등)
                if any(k in ev["type"] for k in ["STARTED", "FAILED", "PAUSED", "RESUMED"]):
                    mark = "❌" if "FAILED" in ev["type"] else "🔹"
                    print(f"{mark} [{ev['sim_time']:07.2f}s] {ev['source']} -> {ev['type']}")