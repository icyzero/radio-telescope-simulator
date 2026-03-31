# tests/integration/test_session_reporter.py

import json
import pytest
from src.sim.session_reporter import SessionReporter

def test_global_report_aggregation(tmp_path):
    # 1. 테스트용 가짜 세션 데이터 생성 (tmp_path 활용)
    reporter = SessionReporter(base_path=tmp_path)
    
    for i, status in enumerate(["SUCCESS", "SUCCESS", "FAILED"]):
        session_dir = tmp_path / f"session_test_{i}"
        session_dir.mkdir()
        with open(session_dir / "session_meta.json", "w") as f:
            json.dump({"status": status, "total_events": 10}, f)

    # 2. 집계 테스트
    stats = reporter.generate_global_stats()
    
    assert stats["total_sessions"] == 3
    assert stats["success_count"] == 2
    assert stats["fail_count"] == 1
    assert stats["success_rate"] == pytest.approx(66.66, abs=0.1)