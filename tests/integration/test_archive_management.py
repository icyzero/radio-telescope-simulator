# tests/integration/test_archive_management.py

import pytest
from src.sim.archive_manager import ArchiveManager

def test_archive_creation_and_metadata():
    archiver = ArchiveManager(base_path="test_storage")
    
    # 가상의 이벤트 기록
    test_event = {"id": 1, "type": "TEST", "payload": {}}
    archiver.log_event(test_event)
    
    # 메타데이터 저장
    summary = {"total_events": 1, "status": "SUCCESS"}
    archiver.save_metadata(summary)
    
    # 검증
    assert archiver.root.exists()
    assert archiver.event_log_path.exists()
    assert (archiver.root / "session_meta.json").exists()