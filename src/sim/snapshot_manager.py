# src/sim/snapshot_manager.py
import json

class SnapshotManager:
    @staticmethod
    def capture(system, last_event_id):
        snapshot = {
            "last_event_id": last_event_id,
            "system_mode": system.mode,
            "managers": {
                name: mgr.get_state() for name, mgr in system.managers.items()
            }
        }
        return snapshot

    @staticmethod
    def save(snapshot, filepath):
        with open(filepath, 'w') as f:
            json.dump(snapshot, f, indent=4)