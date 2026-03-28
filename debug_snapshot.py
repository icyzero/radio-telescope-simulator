# debug_snapshot.py
import json
from src.scheduler.scheduler import SystemController
from src.sim.snapshot_manager import SnapshotManager
from src.controller.command_manager import CommandManager
from src.controller.telescope import Telescope

def check_my_snapshot():
    # 1. 시스템 컨트롤러 생성
    sys = SystemController()
    sys.resume() 

    # 2. 망원경(Telescope) 객체를 먼저 생성합니다. (재료 1)
    tel = Telescope()
    tel.az = 180.0
    tel.alt = 45.0
    
    # 3. 매니저 생성 시 '이름'과 '망원경'을 인자로 넣어줍니다. (재료 2)
    # TypeError 방지: missing 2 required positional arguments 해결
    mgr = CommandManager(name="MgrA", telescope=tel)
    mgr.state = "BUSY"
    
    # 4. 시스템 컨트롤러의 managers 딕셔너리에 등록합니다.
    sys.managers["MgrA"] = mgr

    # 5. 이제 스냅샷을 캡처합니다.
    snap = SnapshotManager.capture(sys, last_event_id=42)

    # 6. 결과 출력
    print("\n--- [Snapshot Data Check] ---")
    print(json.dumps(snap, indent=4))
    print("------------------------------\n")

if __name__ == "__main__":
    check_my_snapshot()