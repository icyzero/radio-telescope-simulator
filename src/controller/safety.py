# src/controller/safety.py

class SafetyGuard:
    # 물리적 한계 정의 (상수로 관리)
    MIN_ALT = 0.0
    MAX_ALT = 90.0
    MIN_AZ = 0.0
    MAX_AZ = 360.0

    @classmethod
    def validate_move(cls, params: dict, current_mode: str):
        """이동 명령의 유효성 검사"""
        # 1. 시스템 모드 체크
        if current_mode in ["STOPPED", "LOCKED"]:
            return False, f"System is in {current_mode} mode. Commands ignored."

        alt = params.get("alt")
        az = params.get("az")

        # 2. 필수 파라미터 존재 여부
        if alt is None or az is None:
            return False, "Missing parameters: alt, az"

        # 3. 물리적 범위 체크
        if not (cls.MIN_ALT <= alt <= cls.MAX_ALT):
            return False, f"Altitude out of range ({cls.MIN_ALT}~{cls.MAX_ALT}): {alt}"
            
        if not (cls.MIN_AZ <= az <= cls.MAX_AZ):
            return False, f"Azimuth out of range ({cls.MIN_AZ}~{cls.MAX_AZ}): {az}"

        return True, "VALIDATED"