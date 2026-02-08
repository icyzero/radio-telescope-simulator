from datetime import datetime
import os

LOG_DIR = "log"
LOG_FILE = os.path.join(LOG_DIR, "telescope.log")

def log(message: str):
    # log 디렉토리 없으면 생성
    os.makedirs(LOG_DIR, exist_ok=True)

    timestamp = datetime.now().isoformat(timespec="seconds")
    line = f"{timestamp} {message}"

    # 콘솔 출력
    print(line)

    # 파일 기록
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")
