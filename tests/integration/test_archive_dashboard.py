# tests/integration/test_archive_dashboard.py

import pytest
from src.sim.archive_dashboard import ArchiveDashboard

def test_dashboard_render_contains_key_info(tmp_path):
    # 1. 테스트용 세션 데이터 생성 (성공 1, 실패 1)
    reporter_path = tmp_path
    (tmp_path / "session_ok").mkdir()
    with open(tmp_path / "session_ok" / "session_meta.json", "w") as f:
        import json
        json.dump({"status": "SUCCESS"}, f)
        
    (tmp_path / "session_fail").mkdir()
    with open(tmp_path / "session_fail" / "session_meta.json", "w") as f:
        json.dump({"status": "FAILED"}, f)
    # 실패 로그 작성
    with open(tmp_path / "session_fail" / "events.jsonl", "w") as f:
        f.write(json.dumps({"type": "FAILED", "sim_time": 10.0, "payload": {"reason": "Test Error"}}) + "\n")

    # 2. 대시보드 렌더링
    db = ArchiveDashboard(storage_path=tmp_path)
    view = db.render()

    # 3. 검증 (주요 키워드가 포함되어 있는가?)
    assert "DASHBOARD" in view
    assert "Total Sessions : 2" in view
    assert "50.0%" in view # 성공률
    assert "Test Error" in view # 에러 사유