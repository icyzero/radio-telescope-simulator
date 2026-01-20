class Command: #명령에 '시간'을 붙일 수 있는 구조
    def __init__(self, alt, az, execute_at=None):
        self.alt = alt
        self.az = az
        self.execute_at = execute_at
    '''excute_at == None → 즉시 실행
       excute_at <= current_time → 실행 가능
       excute_at > current_time → 대기'''