import requests
import time
from datetime import datetime

# 설정
API_BASE_URL = "http://localhost:8000/api/v1"
TASK_ID = "0803be1b-6981-431f-8ce0-335e6df1e3db" # 방금 생성된 ID
LOG_FILE = "e2e_test_result.log"

def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted_message = f"[{timestamp}] {message}"
    print(formatted_message)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(formatted_message + "\n")

def monitor_task():
    log("=== E2E Monitoring Started ===")
    log(f"Tracking Task ID: {TASK_ID}")
    start_time = time.time()
    
    last_progress = ""
    
    while True:
        try:
            status_res = requests.get(f"{API_BASE_URL}/videos/{TASK_ID}/status")
            status_res.raise_for_status()
            status_data = status_res.json()
            
            status = status_data["status"]
            progress = status_data["progress"]
            
            current_progress_str = str(progress)
            if current_progress_str != last_progress:
                log(f"   -> Status: {status}, Progress: {progress}")
                last_progress = current_progress_str
            
            if status == "completed":
                duration = time.time() - start_time
                log(f"   -> [SUCCESS] Task Completed! Total Duration: {duration:.2f}s ({duration/60:.2f}m)")
                break
            
            if status == "failed":
                log(f"   -> [ERROR] Task Failed! Error: {status_data.get('error_message')}")
                break
            
            time.sleep(30) # 1시간짜리니까 30초마다 체크

        except Exception as e:
            log(f"[WARN] Status check failed: {e}")
            time.sleep(30)

    log("=== E2E Monitoring Finished ===")

if __name__ == "__main__":
    monitor_task()
