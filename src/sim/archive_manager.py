# src/sim/archive_manager.py

import os
import json
from pathlib import Path
from datetime import datetime

class ArchiveManager:
    def __init__(self, base_path="storage"):
        # 1. 고유 세션 ID 생성 (시간 기반)
        self.session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.root = Path(base_path) / self.session_id
        self.snap_dir = self.root / "snapshots"
        
        # 2. 폴더 구조 자동 생성
        self.root.mkdir(parents=True, exist_ok=True)
        self.snap_dir.mkdir(parents=True, exist_ok=True)
        
        self.event_log_path = self.root / "events.jsonl"

    def log_event(self, event_dict: dict):
        """이벤트를 JSONL 형식으로 한 줄씩 기록"""
        with open(self.event_log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(event_dict) + "\n")

    def save_metadata(self, summary: dict):
        """세션 종료 시 메타데이터 저장"""
        meta_path = self.root / "session_meta.json"
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=4)