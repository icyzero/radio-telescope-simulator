#src/controller/state_rules.py
from src.controller.enums import TelescopeState, CommandType
from enum import Enum

class CommandDecision(Enum):
    EXECUTE = "EXECUTE"
    PENDING = "PENDING"
    REJECT = "REJECT"


STATE_COMMAND_RULES = {
    TelescopeState.IDLE: {
        CommandType.MOVE: CommandDecision.EXECUTE,
        CommandType.PARK: CommandDecision.EXECUTE,
        CommandType.STOP: CommandDecision.REJECT,
    },
    TelescopeState.MOVING: {
        CommandType.MOVE: CommandDecision.PENDING,
        #CommandType.PARK: CommandDecision.PENDING,
        CommandType.STOP: CommandDecision.EXECUTE,
    },
    TelescopeState.STOPPED: {
        CommandType.MOVE: CommandDecision.REJECT, #STOPPED일 땐 거절
    }
}
