# Radio Telescope Control Simulator

This project is a Python-based simulator for controlling a radio telescope.
The goal is to model telescope motion, scheduling, and observation control.
This repository is part of my preparation for graduate studies in radio astronomy software.


Day 2: Implemented error-based convergence check and automated test

Day 3: Added smooth deceleration + precise target lock-in (all tests passing).

Day 4: Added command queue processing with sequential target execution (multi-target tests passing).

day 6: telescope의 동작 : “외부에서 move_to(x)를 호출하면 Telescope는 목표 좌표를 설정하고 MOVING 상태가 되며, 이후 update()가 반복 호출되면서 현재 위치(alt, az)가 목표 위치 방향으로 점진적으로 변하고, distance < EPSILON 조건이 만족되면 이동을 종료하고 IDLE 상태로 돌아간다.” & 로그 정리

day 8: 위치 제어 → 속도 기반 제어로 개념 분리 시작

Day 9: Implemented time-based simulation loop and visualized telescope motion (Alt/Az vs time, trajectory).

Day 10: Validated velocity-constrained motion model with stable convergence under time-based simulation.

Day 11: Introduced explicit STOP reasons and structured error-state handling for telescope control.

Day 12: Extended command queue with runtime control (cancel, skip, status) for operational use.

Day 15: Project re-entry after illness; reviewed control flow and verified existing simulations without modification.

Day 16: Introduced time-aware command structure as a foundation for scheduling.

Day 17: command.py의 역할을 더 명확히 [Command는 사용자의 의도를 객체로 캡슐화해서 Telescope에 요청하는 역할]/ telescope.py원복(이유: telescope는 순수하게 움직이는 역할만 하기 위해) 

Day 18: Separate command lifecycle from telescope control and validate via tests

Day 19: Introduced timeout-based failure handling for commands, enabling explicit detection and logging of unsuccessful executions.

Day 20: Implemented a CommandManager to execute commands sequentially and manage command lifecycle transitions.

Day 22: Introduced CommandManager to manage command lifecycle, sequencing, and execution flow, separating high-level control logic from Telescope and Command

Day 23: Implemented a main control loop driven by CommandManager, coordinating Telescope updates and sequential command execution.
(아직은 test파일에서 실행하지만 추후에 main.py를 만들예정) 

Day 24: Make main.py

Day 25: Clarified system-level STOPPED state vs command-level ABORTED/FAILED handling, validating robust failure isolation in the control loop.

Day 26: Introduced time-aware command scheduling concept and persistent structured logging to prepare for operational execution.

Day 29: Defined operational command policies, including handling of new commands during motion, pending command cancellation, and explicit separation between command intent and physical state logs.

Day 30: Refined command acceptance rules by introducing explicit EXECUTE, PENDING, and REJECT decisions based on telescope state.
This clarified the distinction between rejected commands and aborted executions, and laid the groundwork for future priority-based scheduling.

Day 31: Introduced command-level scheduling metadata by adding scheduled_at and priority attributes to commands, and updated the CommandManager to sort pending commands accordingly.
This established the foundation for deterministic command ordering and future scheduling policy extensions.

Day 32: Formalized the conceptual distinction between STOP and regular operational commands.
STOP was redefined as a system-level interrupt rather than a queued command, ensuring immediate flow interruption and preventing unsafe coupling with normal command lifecycle rules.

Day 33: Expanded and validated execution scenarios (including interrupt and cancellation paths) to verify correct command flow under dynamic conditions.
This confirmed that command execution, interruption, and cleanup behavior remained consistent across multiple edge cases.

Day 34: Clarified architectural responsibilities across Command, CommandManager, and Telescope components.
Explicitly defined what each layer is allowed to know and control, and identified STOP handling as the most critical coupling point requiring centralized management.

Day 35: Consolidated design principles through structured review and mental simulation of command flows.
This day focused on stabilizing architectural boundaries, reinforcing safety-critical assumptions, and ensuring the system can be extended without violating core responsibility separations.

Day 36: locks down architectural boundaries before adding further system complexity.

Day 40: Added a thin SystemController to support multi-telescope coordination without breaking flow ownership.
Preserved execution isolation per device and intentionally avoided global state coupling.

Day 41: Formalized observability principles across Command, CommandManager, and SystemController layers.
Redefined logs as operational artifacts rather than debug outputs, ensuring that execution flow, decision points, and system-level policy events can be reconstructed solely from structured log records.
Established strict logging boundaries per architectural layer to preserve separation of responsibilities while maintaining full traceability.

Day 43: Evaluated the system’s testability across all architectural layers.
Confirmed that Telescope, Command, and CommandManager components can be unit-tested independently through interface isolation and controlled test doubles.
Identified the boundary between unit and integration testing, particularly for STOP race conditions and global policy propagation scenarios.
Established a clear verification strategy to ensure architectural integrity under edge and interrupt-driven conditions.

Day 44: Implemented the first concrete unit tests targeting the Telescope layer.
Validated state transitions, motion convergence, and STOP latch behavior under controlled update cycles.
Confirmed that the physical layer is fully isolated and independently testable without dependencies on higher architectural layers.

Day 45: Implemented unit tests for the Command layer using a controlled FakeTelescope.
Verified command delegation, state transitions to SUCCESS and ABORTED, and confirmed strict interface-based interaction with the physical layer.
Established Command as an isolated state machine independent from Manager and System layers.

Day 46: Implemented unit tests for the CommandManager layer using controlled FakeCommand and FakeTelescope objects.
Validated command acceptance rules, queue behavior, execution sequencing, and immediate STOP intervention handling.
Confirmed CommandManager’s role as a flow orchestrator rather than a state machine.

Day 47: Implemented full integration tests covering multi-manager execution and global STOP propagation.
Verified end-to-end policy flow from SystemController down to Telescope.
Established STOP-first priority policy under SUCCESS race conditions.
Confirmed architectural integrity across physical, command, orchestration, and policy layers.

Day 48: Refactored the test suite structure to clearly separate unit and integration layers.
Introduced reusable fixtures and improved naming consistency for long-term maintainability.
Transitioned the project from feature validation to structural stabilization.

Day 50: Introduced defensive and failure-path tests.
Validated system behavior under STOPPED state, FAILED commands, zero and large dt values, and post-STOP command attempts.
Transitioned the architecture toward fail-safe guarantees.
Refactored and updated the telescope's update method.
  - Unified movement logic
  - Removed duplicated position update
  - Added vector-based clamping
  - Stabilized state transitions

Day 51: Introduced PAUSE/RESUME operational mode.
Distinguished between fail-safe STOP and state-preserving PAUSE.
Enabled safe runtime suspension without destroying execution context.

Day 52: Introduced structured event logging layer.
Enabled observability for command lifecycle and system mode transitions.
Separated control logic from monitoring concerns.

Day 53: Strengthened state machine guarantees through stability tests.
Enforced strict command lifecycle ordering (STARTED → SUCCESS).
Validated pause/resume invariants to ensure deterministic control flow.

Day 54: Finalized manager-level failure containment boundary.
Validated lock integrity and ensured critical events are emitted exactly once.
Sealed post-failure execution path to guarantee deterministic shutdown behavior.

Day 55: Implemented controlled recovery mechanism after critical lock.
Introduced reset pathway strictly gated by LOCKED state.
Ensured minimal-impact state restoration by clearing only critical flags.
Preserved configuration integrity and prevented duplicate critical event emission.
Established deterministic re-entry boundary for post-failure operation.

Day 57: Began explicit state machine refactoring.
Separated state-dependent behaviors from Telescope core logic.
Laid groundwork for formal State Pattern integration.

Day 58: Validated State Pattern extensibility.
Introduced PausedState without modifying existing state logic.
Confirmed open-closed compliance through isolated state testing.
Established scalable state transition foundation.

Day 59: Evolved EventBus into an observer-based dispatcher.
Introduced subscription mechanism for reactive event handling.
Decoupled event emission from event consumption.
Enabled scalable monitoring and extension architecture.

Day 60: Introduced publish–subscribe EventBus for system-wide event propagation.
Enabled targeted event routing with type-based subscriptions.
Added in-memory event history to support observability and debugging.

Day 61: Stabilized event structure using enum-based event types and dict payloads.
Payload dictionaries allow flexible extension and easy JSON serialization for future monitoring integrations.
Event history tracking confirmed through tests.

Day 62: Improved event observability by adding readable event formatting
and a logging subscriber. Events now include simulation time and wall time,
making system behavior easier to trace and debug.

Day 64: Introduced command lifecycle events.
Scheduler now publishes events when commands start and finish,
allowing the system to track command execution through EventBus.

Day 65: Introduced an EventLogger subscriber that listens to
EventBus events and records them for observability and debugging.

Day 66: Introduced EventMetrics subscriber that listens to command lifecycle
events and collects execution statistics such as started and successful commands.

Day 67: Added EventTimeline utility to analyze event history
and compute execution durations between command lifecycle events.

Day 68: Introduced event query capability in EventBus,
allowing filtering of events by type, source, and simulation time.

Day 69: Implemented EventReplay utility to replay
recorded event history while preserving event order
and command lifecycle events.

Day 70: System architecture review.
Consolidated understanding of command lifecycle,
manager state machine, and event observability layer.

Day 71: Added event persistence layer to export
event history to JSON files for external analysis
and long-term storage.

Day 72: Added event loading capability to restore
event history from JSON files, enabling replay
and external simulation reconstruction.

Day 73: Implemented event-driven system replay
to reconstruct system state from event history.

Day 74: Introduced event validation layer to ensure
data integrity and prevent invalid events from
affecting system replay.

Day 75: Enforced strict event validation in EventBus
to prevent invalid events from being published and ensure event log integrity for reliable replay.

Day 76: Introduced event versioning to support schema evolution
and ensure backward compatibility for future replay.

Day 78: Implemented replay determinism test
and verified consistent state reconstruction for basic simulation scenarios.

Day 79: Enforced required state information in event payload
to ensure accurate and complete state reconstruction during replay.

Day 80: Implemented replay coverage tests for multi-event scenarios
to verify system consistency and correctness across complex event sequences.

Day 81: Strengthened event versioning by enforcing replay failure
for unsupported future versions to ensure system safety and compatibility.

Day 82: Implemented event versioning and multi-version validation
to ensure backward compatibility for v1 logs while enforcing strict schemas for v2 data.

Day 83: Implemented Snapshot system and Hybrid Recovery mechanism
to enable rapid state reconstruction by combining point-in-time snapshots with delta events.

Day 85: Implemented ArchiveManager for session-based data management
to isolate simulation datasets and preserve session metadata for long-term observability.

Day 86: Implemented SessionReporter for global simulation analytics
to aggregate multi-session results and provide high-level statistics such as success rates.

Day 87: Implemented SessionInspector for automated error tracing
to extract precise failure reasons and timestamps from session logs, enhancing debuggability.

Day 88: Built an integrated CLI Archive Dashboard
by combining SessionReporter and SessionInspector to provide a centralized view of simulation health and failure analysis.

Day 89: Implemented a high-precision TimeController with dynamic scaling
to support accelerated simulation and maintain temporal continuity during real-time scale transitions.

Day 90: Integrated RemoteCommandGate for external JSON command injection
to decouple the simulation engine from direct method calls and enable remote orchestration.

Day 92: Validated Telemetry Data Integrity via RemoteCommandGate.
Confirmed that external MOVE commands correctly trigger physical motion and 
that telescope state (Az/Alt) can be precisely tracked during simulation updates.

Day 93: Implemented TelemetryStreamer with fixed-interval broadcasting.
Validated that simulation state packets are generated at precise intervals (0.1s)
independent of the underlying update() cycle, ensuring consistent real-time observability.

Day 94: Implemented Adaptive Telemetry Streaming.
Engine now dynamically switches between Heartbeat mode (1.0s) and Burst mode (0.1s) 
based on telescope activity. Added immediate event-driven push for critical failures, 
ensuring zero-latency reporting for system errors.

Day 95: Implemented SafetyGuard layer within RemoteCommandGate.
Added strict range validation for coordinates (Alt/Az) and system-state awareness 
to reject incoming commands during STOPPED or invalid operational modes. 
Enhanced system robustness by filtering malformed or unsafe requests at the entry point.

Day 96: Implemented Dynamic Configuration Update (Hot-Reload).
Enabled real-time tuning of physical parameters (e.g., slew_rate) via RemoteCommandGate.
Integrated SafetyGuard to validate configuration changes, preventing unsafe 
parameter injections without restarting the simulation.

Day 97: Implemented Comprehensive System Diagnostics API.
The system now provides a unified JSON report including operational modes, 
hardware configurations, and performance metrics (e.g., command success rates).
Validated real-time update of failure statistics through the Diagnostics interface.

Day 99: Conducted Final Stress & Chaos Test.
Validated system stability under a high-load environment (100+ rapid-fire commands).
Confirmed seamless interaction between real-time config tuning, diagnostics, 
and safety-guard filtering during active telescope motion.

Day 100: Grand Finale - Full System Integration & Live Demonstration.
Successfully executed the final mission scenario, integrating the entire control 
architecture: Remote Gateway, Safety Guard, Command Manager, and Adaptive Streamer.
The project concludes with a 100% stable platform capable of real-time tuning, 
autonomous defense against invalid inputs, and comprehensive health reporting.
Mission Accomplished.

Day 101: Initiated Signal Processing Phase.
Implemented VirtualSDR for generating synthetic IQ (In-phase/Quadrature) data.
Developed SignalProcessor with FFT (Fast Fourier Transform) and windowing 
(Blackman window) to analyze power spectrum. 
Established the foundation for SDR integration during the hardware delivery period.

Day 102: Implemented Real-time Spectrum Visualizer.
- Integrated Matplotlib's FuncAnimation for live signal monitoring.
- Visualized 500kHz synthetic signal at 60dB PSD in a dynamic environment.
- Verified FFT-shift and Decibel(dB) scale conversion logic.
- Observed real-time noise floor and signal-to-noise ratio (SNR) visually.

Day 103: Advanced Signal Visualization - Waterfall Display.
- Implemented 2-tier UI: Live Spectrum (Top) and Waterfall Chart (Bottom).
- Simulated frequency-modulated(FM) signals with a time-varying dynamic frequency.
- Successfully captured the 'S-curve' trajectory of a shifting signal source.
- Validated time-frequency domain correlation for celestial tracking simulation.

Day 104: Data Persistence & Standardization.
- Integrated 'astropy.io.fits' for astronomical data standardization.
- Implemented a dual-recording system: High-fidelity FITS for analysis and PNG for snapshots.
- Added interactive keyboard triggers ('S' key) for on-demand data archiving.
- Established a structured naming convention based on observation timestamps.

Day 105: Quantitative Signal Analysis & Verification.
- Processed archived FITS data to extract signal-to-noise ratio (SNR) and drift metrics.
- Verified signal tracking consistency by overlaying 'Tracked Path' on Waterfall data.
- Achieved Peak SNR of 27.48 dB, confirming high-fidelity simulation and recovery.
- Established a basic scientific reporting pipeline for future real-world SDR data.

Day 106: Doppler De-drifting & Signal Integration.
- Successfully implemented a 'SignalStraightener' using numpy.roll to correct frequency drift.
- Transformed a dispersed 'U-shaped' spectrum (Raw) into a sharp, focused peak (De-drifted).
- Achieved a significant boost in Signal-to-Noise Ratio (SNR) by concentrating energy from 300+ bins into a single spectral channel.
- Validated the signal recovery pipeline, a critical requirement for SETI and Pulsar research.

Day 108: Interactive Hardware Control & Gain Management.
- Implemented SDRFactory for seamless switching between Real/Virtual SDR modes.
- Integrated real-time Gain control (UP/DOWN keys) into the visualization pipeline.
- Verified dynamic signal response: Observed proportional increase in PSD/Waterfall intensity relative to gain levels.
- Prepared error-handling for hardware disconnection (Fallback to VirtualSDR).

Day 109: Observation Automation & Sequential Scheduling.
- Developed an Automated Scheduler to execute multi-session observation plans.
- Implemented ON-OFF source switching logic for background noise subtraction.
- Integrated thread-safe logging system for observation history tracking.
- Successfully automated the full pipeline: Frequency tuning -> Data capture -> FITS Archiving.

Day 110: Full System Integration & Multi-Manager Deployment.
- Final Integration of Signal Processing, Visualizer, Scheduler, and Safety Guard.
- Implemented Multi-Telescope control architecture (Manager A & B simultaneous tracking).
- Enhanced system reliability with a Command-Gate pattern and real-time Safety Guard.
- Achieved a stable observation pipeline with 75% success rate in diagnostic stress tests.
- Established the core 'Control Center v1.1' for future hardware-in-the-loop (HIL) testing.

Day 113: Pure Global Environment Integration & First Light.
- Deployed RTL-SDR Blog V4 hardware and achieved native execution without local virtual environments.
- Resolved runtime `AttributeError` (rtlsdr_set_dithering) by downgrading `pyrtlsdr` to a stable version (0.3.0).
- Fixed Windows DLL search restrictions by incorporating `os.add_dll_directory` targeting the root `rtlsdr.dll`.
- Verified 100% stable global pipeline execution: Successfully captured 1,024 real RF samples.
- Permanently optimized project directory size by removing local `venv` dependencies, making it portfolio-ready.

Day 114: Hardware Calibration & Digital Signal Processing (DSP)
- **Problem Diagnosed**: Identified a critical Zero-IF architecture limitation—**DC Offset (LO Leakage)**—causing a severe artificial peak and vertical artifact at the center frequency ($0.0 \text{ MHz}$) during live hardware streaming.
- **DSP Solution Implemented**: Integrated an **IQ Mean Subtraction** algorithm into the real-time data acquisition pipeline. By calculating and mitigating the empirical DC bias ($\mu_I, \mu_Q$) from raw complex samples, the center hardware noise floor was successfully flattened.
- **System Outcome**: Cleared the central observation band, drastically improving the Signal-to-Noise Ratio (SNR) and enabling artifact-free data logging for the target 21cm Neutral Hydrogen Line ($1420.4 \text{ MHz}$) profile.
- **Architecture Integrity**: Maintained modular encapsulation without breaking the legacy motor simulation or the Day 100 `SignalStraightener` analytical sub-routines.

Day 115: Automated Gain Optimization & RFI Site Survey (Completed)
- **SDR Artifact Isolation**: Detected and bypassed the `0.0 dB` hardware initialization anomaly (driver-level clipping mimicry at `-9.01 dB`).
- **Dynamic Range Mapping**: Swept operational gains from $3.7 \text{ dB}$ to $49.6 \text{ dB}$. Documented a clean local electromagnetic environment with an ambient noise floor scaling safely from $-44.05 \text{ dB}$ to $-38.44 \text{ dB}$.
- **Optimal Gain Lock**: Officially locked the system's baseline acquisition profile at **$49.6 \text{ dB}$**—maximizing the Low-Noise Amplifier (LNA) sensitivity without front-end saturation, tailored for 21cm Hydrogen line captures.

Day 116: Doppler Astro-Engine Integration (Completed)
- **Doppler Shift Velocity Mapping**: Developed a specialized `DopplerAstroEngine` translating raw radio frequency spectrum arrays directly into Galactic line-of-sight velocity parameters ($\text{km/s}$).
- **Astrophysical Standardization**: Synced the $1420.40575 \text{ MHz}$ neutral hydrogen rest-frame ($f_{\text{rest}}$) with real-world target profiles captured via the RTL-SDR Blog V4 hardware.
- **Dynamic Bandwidth Profiling**: Verified a calibrated velocity resolution band sweeping from **$-251.8 \text{ km/s}$ (Approaching/Blueshift)** to **$+254.5 \text{ km/s}$ (Receding/Redshift)** across the $2.4 \text{ MHz}$ instantaneous bandwidth.
- **Data Product Evolution**: Transformed the simulator pipeline output from standard RF signal power into scientific line profiles, clearing paths for observational verification of galactic spiral arm rotation dynamics.

Day 117: Production-Ready UI Optimization & Hardware Gain Step Mapping
- **UI Architecture Robustness**: Resolved a critical Matplotlib runtime crash (`AttributeError: 'float' object has no attribute 'view'`) triggered by cursor tracking telemetry during mouse-drag events over the Doppler canvas.
- **Buffer Initialization Fix**: Eradicated the waterfall display corruption anomaly (the fragmented yellow-black dummy mosaic pattern) by introducing a fail-safe array boundary filter during dynamic frequency hopping sequences.
- **Hardware Gain Step-Mapping**: Restructured the raw receiver LNA controls into a standardized **6-Step Precision Mapping Interface (1/6 to 6/6)**, aligning discrete software hotkeys perfectly with the optimal physical profiles of the RTL-SDR Blog V4 ($0.0 \text{ dB}$ to $49.6 \text{ dB}$).
- **Observational Science Verification**: Successfully detected a distinct, persistent emission profile concentrated at the **$-125 \text{ km/s}$** velocity corridor, providing verified observational tracking of high-velocity Galactic spiral arm structures.
---------------------------------------------------------
## How to Run

This project is executed through a main control loop.

```bash
python -m src.main
```


## Execution Flow

- Initialize Telescope and CommandManager
- Queue commands in CommandManager
- Main loop continuously updates:
  - CommandManager (command lifecycle)
  - Telescope (physical movement simulation)
- System remains running, awaiting further commands

## Log Format

The system uses simple console logs to represent execution state.

- [CMD]   : Command lifecycle (START / RUNNING / SUCCESS / FAILED)
- [STATE] : Telescope state transitions
- [SYSTEM]: System-level startup or shutdown messages
- [INFO]  : General execution flow

Example:

[SYSTEM] Telescope control system started
[CMD] MoveCommand START
[STATE] IDLE → MOVING

---------------------------------------------------------
## System Design Philosophy

This simulator is structured to resemble a real-world telescope control system,
where time continuously flows and the system reacts to commands and events.

- **Telescope**
  - A passive physical model.
  - Responsible only for updating its internal state (position, motion, STOPPED).
  - Has no knowledge of commands or execution order.

- **Command**
  - Encapsulates user intent (e.g., move, stop).
  - Defines execution logic and success/failure conditions.
  - Does not control time or scheduling.

- **CommandManager**
  - Owns command sequencing and lifecycle management.
  - Decides *what* command runs and *when*.
  - Acts as the central controller between user intent and physical motion.

- **Main Control Loop**
  - Simulates real-time flow using a fixed `dt`.
  - Continuously updates both the Telescope and CommandManager.
  - Designed as an infinite loop to reflect always-on control systems.
  - System termination is driven by state (e.g., STOPPED), not by loop structure.

-----------------------------------------------------------------------
### Logging Policy

- [CMD]    : Operator / Scheduler intent (Command lifecycle)
- [STATE]  : Physical or simulated telescope state change
- [SYSTEM] : Control flow, safety, scheduling decisions
- [INFO]   : Non-critical reference information

-------------------------------------------------------------------
## Scheduling Policy

Commands are scheduled based on explicit priority levels.
Lower numeric values indicate higher priority.

- STOP commands have the highest priority and are executed as soon as possible.
- MOVE commands are executed sequentially when the telescope is available.
- PARK commands are deferred until motion completes.

This policy reflects real-world telescope safety and operational constraints.

-----------------------------------------------------------------
## STOP Command Policy

STOP is treated as an interrupt-type command rather than a scheduled task.
It can be issued at any time to immediately halt telescope motion,
regardless of the current command execution state.

STOP does not represent a normal success or failure outcome.
Instead, it forces a state transition to a safe STOPPED condition,
reflecting an operator-level safety intervention.

------------------------------------------------------------
## Logging Responsibility

Logs are categorized by responsibility to clarify system behavior.

| Tag      | Responsibility |
|----------|----------------|
| [CMD]    | Command intent, execution, and termination |
| [STATE]  | Physical state transitions of the telescope |
| [SYSTEM] | System-level control flow and safety handling |

This separation helps distinguish operator intent,
mechanical state changes, and controller-level decisions.
-------------------------------------------------------------
## Operational Scenarios

This system is designed from an operational control perspective,
focusing on safety and fault isolation.

Key guarantees:
- STOP commands immediately interrupt ongoing operations.
- Command failures are contained within command execution.
- Telescope physical state remains consistent after failures.
- The system prioritizes safety over command completion.

--------------------------------------------------------------
## Responsibility Boundary (Why this is a Control System)

이 시스템은 명령 실행기가 아니라 관제 시스템이다.
Command는 의도를 표현하고, Telescope는 상태를 책임지며,
CommandManager는 전체 실행 흐름과 안전을 통제한다.

-----------------------------------------------------------
Logs are treated as runtime artifacts and stored separately
from source code to reflect operational usage.

----------------------------------------------------------
