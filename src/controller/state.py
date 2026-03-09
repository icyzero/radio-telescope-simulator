# src/controller/state.py
from src.sim.event import EventType
from src.utils.logger import log
from src.controller.state_rules import STATE_COMMAND_RULES, CommandDecision
from src.controller.command import (
    CMD_SUCCESS,
    CMD_FAILED,
    CMD_ABORTED,
)
from src.controller.command import ResetCommand

class ManagerState:
    """모든 상태 객체의 추상 인터페이스"""
    def handle_add_command(self, manager, cmd, system_mode):
        """새 명령이 들어왔을 때의 행동"""
        raise NotImplementedError

    def handle_update(self, manager, dt):
        """매 틱(Tick)마다의 행동"""
        raise NotImplementedError

    def handle_reset(self, manager):
        """리셋 시도가 들어왔을 때의 행동"""
        raise NotImplementedError

class IdleState(ManagerState):
    def handle_add_command(self, manager, cmd, system_mode):
        # 1. 하드웨어 상태 확인
        tele_state = manager.telescope.state
        log(f"[DEBUG] add_command: state={tele_state.name}, cmd={cmd.type.name}", prefix=manager.name)

        # 2. 시스템 모드 확인 (PAUSED 등)
        system_mode = manager.get_system_mode()

        if system_mode == "PAUSED":
            decision = CommandDecision.PENDING
        else:
            # STATE_COMMAND_RULES는 외부 설정이므로 그대로 참조하거나 manager를 통해 접근
            decision = STATE_COMMAND_RULES[tele_state].get(cmd.type, CommandDecision.REJECT)

        # 3. 결정에 따른 동작 수행
        if decision == CommandDecision.EXECUTE:
            log(f"[CMD] {cmd.type.name} accepted ({decision.name})", prefix=manager.name)
            if manager.current:
                manager.current.abort(prefix=manager.name)
            
            manager.queue.clear()
            manager.current = cmd
            manager.emit(EventType.COMMAND_STARTED, manager.name, {
                "cmd_type": type(manager.current).__name__,
                "scheduled_at": manager.time
            })
            # [Day 64 핵심 수정] 즉시 실행 시 발생하는 에러를 여기서 잡아야 함!
            try:
                cmd.execute(manager.telescope, prefix=manager.name)
            except Exception as e:
                # 📢 EVENT: COMMAND_FAILED 발행
                manager.emit(EventType.COMMAND_FAILED, manager.name, {
                    "cmd_type": type(cmd).__name__,
                    "error": str(e)
                })
                manager.current = None # 에러 났으니 점유 해제
                # 에러를 잡았으므로 여기서 조용히 리턴합니다.
                return
            
        elif decision == CommandDecision.PENDING:
            manager.queue.append(cmd)
            manager.queue.sort(key=lambda c: c.priority)
            log(f"[CMD] {cmd.type.name} accepted ({decision.name})", prefix=manager.name)

        else: # REJECT
            log(f"[CMD] {cmd.type.name} rejected (state={tele_state.name})", prefix=manager.name)

    def handle_update(self, manager, dt):
        if dt <= 0: # 🔒 이미 락이 걸렸다면 업데이트 중단
            return
        
        manager.time += dt
        
        # 🔄 추가: 모드 변경 감지 시 즉시 상태 전이
        if manager.get_system_mode() == "PAUSED":
            log(f"[{manager.name}] Mode changed: IDLE -> PAUSED", prefix=manager.name)
            manager.state = PausedState()
            return  # 상태가 바뀌었으므로 이번 루프 종료

        # 1. 실행 중인 Command가 없으면 다음 Command 실행
        if manager.current is None and manager.queue:
            next_cmd = manager.queue[0]
            
            if manager.time >= next_cmd.scheduled_at:
                manager.current = manager.queue.pop(0)
                # 📢 EVENT: COMMAND_STARTED
                manager.emit(EventType.COMMAND_STARTED, manager.name, {
                    "cmd_type": type(manager.current).__name__,
                })
                # [Day 64 추가] 명령 시작 시 발생할 수 있는 즉각적 에러 방어
                try:
                    manager.current.execute(manager.telescope, prefix=manager.name)
                except Exception as e:
                    manager.emit(EventType.COMMAND_FAILED, manager.name, {
                        "cmo_type": type(manager.current).__name__,
                        "error": str(e)
                    })
                    manager.current = None # 에러 시 점유 해제
                    return

        if manager.current:
            # [Day 64 추가] 매 틱 업데이트 중 발생하는 에러 방어
            try:
                manager.current.update(manager.telescope, dt, prefix=manager.name)
            except Exception as e:
                manager.emit(EventType.COMMAND_FAILED, manager.name, {
                    "cmd_type": type(manager.current).__name__,
                    "error": str(e)
                })
                manager.current = None
                return

            # 2. Command 종료 처리 (Day 64 기존 로직 보완)
            if manager.current.state in (CMD_SUCCESS, CMD_FAILED, CMD_ABORTED):
                final_state = manager.current.state
                
                # SUCCESS/FAILED/ABORTED에 따른 정확한 이벤트 발행
                if final_state == CMD_SUCCESS:
                    manager.emit(EventType.COMMAND_SUCCESS, manager.name, {"cmd_type": type(manager.current).__name__})
                else:
                    # FAILED나 ABORTED는 모두 광의의 실패(FAILED)로 기록
                    manager.emit(EventType.COMMAND_FAILED, manager.name, {
                        "cmd_type": type(manager.current).__name__,
                        "reason": final_state # ABORTED인지 FAILED인지 페이로드에 남김
                    })

                # 💡 정책: 실패(FAILED)하거나 하드웨어가 멈춘 경우 처리
                if final_state == CMD_FAILED or manager.telescope.is_stopped():
                    reason = "FAILED" if final_state == CMD_FAILED else "STOPPED"
                    
                    manager.state = LockedState() # 🔒 락 활성화
                    # 📢 EVENT: 시스템 중단 유발 이벤트
                    manager.emit(EventType.MANAGER_CRITICAL_STOP, manager.name, {"reason": reason})
                    
                    manager.current = None # 이 위치가 중복 방지의 핵심
                    manager.queue.clear()
                    return

                # 4. 정상적인 Command 종료 → 다음 Command로
                manager.current = None

    def handle_reset(self, manager):
        """
        IDLE 상태에서 리셋 시도가 올 경우: 
        이미 정상이므로 아무 작업도 하지 않고 로그만 남깁니다.
        """
        log(f"[{manager.name}] Reset ignored: Manager is already in IDLE state.", prefix=manager.name)
        return  # 에러 없이 정상 종료

class LockedState(ManagerState):
    def handle_add_command(self, manager, cmd, system_mode):
        # LOCKED일 때는 무조건 거절 (Day 54의 원칙)
        manager.emit(EventType.INVALID_COMMAND, manager.name, {"reason": "MANAGER_LOCKED"})
        log(f"[{manager.name}] REJECT: Manager is LOCKED.", prefix=manager.name)

    def handle_update(self, manager, dt):
        # LOCKED 상태에서는 아무것도 하지 않음 (Day 53의 원칙)
        return
    
    def handle_reset(self, manager):
        # 🔒 락을 해제하고 다시 Idle 상태로 복구
        
        reset_cmd = ResetCommand()
        reset_cmd.execute(manager.telescope, prefix=manager.name)
        
        manager.state = IdleState() # 🚀 상태 복구!
        manager.emit(EventType.SYSTEM_RESUMED, manager.name, {"reason": "OPERATOR_RESET"})
        log(f"[{manager.name}] Manager unlocked and returned to IDLE.", prefix=manager.name)

class PausedState(ManagerState):
    def handle_add_command(self, manager, cmd, system_mode):
        # ⏸️ 일시정지 중에는 명령을 실행하지 않고 큐에 '보관(PENDING)'만 합니다.
        manager.queue.append(cmd)
        manager.queue.sort(key=lambda c: c.priority)
        log(f"[{manager.name}] PAUSED: Command queued as PENDING.", prefix=manager.name)

    def handle_update(self, manager, dt):
        # ⏸️ 시간은 흐르지만, 새로운 명령을 꺼내거나 실행하지는 않습니다.
        manager.time += dt
        # manager.current가 있다면 그것만 업데이트 (하던 건 마저 함)
        if manager.current:
            manager.current.update(manager.telescope, dt, prefix=manager.name)
        
        # 🔄 상태 전이 체크: 다시 NORMAL이 되면 IdleState로 복구!
        if manager.get_system_mode() == "NORMAL":
            log(f"[{manager.name}] Mode changed: PAUSED -> IDLE", prefix=manager.name)
            manager.state = IdleState()
            
    def handle_reset(self, manager):
        # 일시정지 중 리셋은 무시하거나 IDLE로 복귀시킬 수 있습니다.
        log(f"[{manager.name}] Reset in PAUSED: Returning to IDLE.", prefix=manager.name)
        manager.state = IdleState()