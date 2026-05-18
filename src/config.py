#src.config.py

# 관측 파라미터 설정
CONFIG = {
    "SAMPLE_RATE": 2.4e6,
    "CENTER_FREQ": 1420.4e6,    # 21cm Hydrogen Line (수소선)
    "GAIN_DEFAULT": 49.6,       # 💡 Day 115: 실전 스캔 결과 반영 (0.0dB 버그 회피 및 최대 증폭)
    "HISTORY_SIZE": 150,
    "OBS_PATH": "./observations/",
    "SDR_MODE": "real"          # "real", "virtual", "auto" 중 선택
}