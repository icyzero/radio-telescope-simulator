def capture_system_state(system):
    """비교 가능한 순수 상태 데이터만 추출"""
    state_snapshot = {
        "system_mode": system.mode,
        "sim_time": round(system.sim_time, 4),
        "managers": {}
    }

    for name, mgr in system.managers.items():
        # 매니저의 상태가 Enum이면 .name을, 아니면 문자열로 변환
        mgr_state = mgr.state.name if hasattr(mgr.state, 'name') else str(mgr.state)
        state_snapshot["managers"][name] = {
            "state": mgr_state,
            "queue_size": len(mgr.command_queue) if hasattr(mgr, 'command_queue') else 0
        }
    
    return state_snapshot