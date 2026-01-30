from datetime import datetime

LOG_FILE = "telescope.log"

def log(message: str):
    timestamp = datetime.now().isoformat(timespec="seconds")
    line = f"{timestamp} {message}"

    # 콘솔 출력
    print(line)

    # 파일 기록
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")
