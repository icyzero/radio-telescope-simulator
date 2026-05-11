# 관측 파라미터 설정
CONFIG = {
    "SAMPLE_RATE": 2.4e6,
    "CENTER_FREQ": 1420.4e6,    # 21cm Hydrogen Line (수소선)
    "GAIN_DEFAULT": 20.0,
    "HISTORY_SIZE": 150,
    "OBS_PATH": "./observations/",
    "SDR_MODE": "auto"          # "real", "virtual", "auto" 중 선택
}