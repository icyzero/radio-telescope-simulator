1. 시스템 개요(System Overview)
Radio Telescope Simulator는 비동기 이벤트 기반의 전파 망원경 제어 시스템.
    ●Top Layer: SystemController (중앙 관제)
    ●Middle Layer: Scheduler & CommandManager (스케줄링 및 명령 관리)
    ●Bottom Layer: TelescopeHardware (하드웨어 추상화)

2. 명령 흐름(Command Flow)
명령이 입력되어 실행되기까지의 여정을 기록
    1. USER -> CommandManager.add_command()
    2. Scheduler -> 매 틱마다 실행 가능한 명령 확인
    3. Command.execute() -> 하드웨어 제어 시작
    4. EventBus.publish() -> 상태 변화 알림

3. 상태머신(State Machine)
CommandManager가 명령을 어떻게 처리하는지 논리 구조를 적습니다.
    ● IDLE: 대기 중
    ● RUNNING: 명령 수행 중
    ● PAUSED: 일시 정지 (상태 보존)
    ● ERROR: 장애 발생 및 복구 대기

    stateDiagram-v2
        [*] --> IDLE
        IDLE --> RUNNING : Command Added / Tick
        RUNNING --> PAUSED : Pause Signal
        PAUSED --> RUNNING : Resume Signal
        RUNNING --> IDLE : Command Success
        RUNNING --> ERROR : Hardware Fault
        ERROR --> IDLE : Reset
    
4. 이벤트 버스 아키텍처(EventBus Architecture)

    ● Pub/Sub 모델: 발행자와 구독자가 서로를 몰라도 소통 가능 (Decoupling)
    ● 이벤트 구조: EventType, Source, Payload, Timestamp 포함
    ● 관측 가능성: 모든 이벤트는 _history에 기록되어 사후 분석 가능