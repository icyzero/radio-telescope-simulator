# debug_dashboard.py
from src.sim.archive_dashboard import ArchiveDashboard

if __name__ == "__main__":
    # 실제 storage 폴더 경로를 지정하세요.
    db = ArchiveDashboard(storage_path="test_storage")
    db.run_loop()