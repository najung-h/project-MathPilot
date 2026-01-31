"""
Integration Test for VideoProcessingService
"""

import asyncio
import sys
import os
import uuid
from pathlib import Path
from datetime import datetime, timezone

# Logging Setup
class Tee(object):
    def __init__(self, original_stream, log_file):
        self.original_stream = original_stream
        self.log_file = log_file

    def write(self, message):
        self.original_stream.write(message)
        self.log_file.write(message)
        self.log_file.flush()

    def flush(self):
        self.original_stream.flush()
        self.log_file.flush()

# Open log file and redirect stdout/stderr
log_file = open("integration_test.log", "w", encoding="utf-8")
sys.stdout = Tee(sys.stdout, log_file)
sys.stderr = Tee(sys.stderr, log_file)

# backend 경로 추가
sys.path.append(str(Path("backend").resolve()))

# .env 로드
from dotenv import load_dotenv
load_dotenv(Path("backend/.env"))

from app.services.video_service import VideoProcessingService
from app.config import settings, get_settings

# 설정 디버깅 및 강제 재설정
print(f"[DEBUG] Loaded LLM_PROVIDER: {settings.LLM_PROVIDER}")
if settings.LLM_PROVIDER != "nvidia":
    print("[WARN] LLM_PROVIDER is not 'nvidia'. Forcing override...")
    os.environ["LLM_PROVIDER"] = "nvidia"
    get_settings.cache_clear() # 캐시 초기화
    # settings 객체는 이미 import 되었으므로 모듈 레벨 변수 업데이트 필요
    # 그러나 import 된 settings는 불변일 수 있으므로 deps에서 get_settings() 호출 시점엔 반영될 것임
    print(f"[DEBUG] New LLM_PROVIDER: {get_settings().LLM_PROVIDER}")

# 가짜 Task Store
_task_store = {}

async def test_integration():
    # 1. 테스트 비디오 파일 준비 (prepare_and_test.py에서 만든 short_test.mp4 사용)
    test_video_path = Path("downloads_test/short_test.mp4")
    if not test_video_path.exists():
        print("[ERROR] Run prepare_and_test.py first to generate short_test.mp4")
        return

    # 2. 가상의 Task 생성
    task_id = str(uuid.uuid4())
    print(f"[TEST] Created Task ID: {task_id}")
    
    # 파일을 storage 경로로 복사 (업로드 시뮬레이션)
    storage_path = Path(settings.STORAGE_PATH)
    video_key = f"videos/{task_id}/original.mp4"
    dest_path = storage_path / video_key
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    
    import shutil
    shutil.copy2(test_video_path, dest_path)
    print(f"[TEST] Uploaded video to: {dest_path}")

    _task_store[task_id] = {
        "status": "processing",
        "s3_key": video_key,
        "filename": "Integration Test Video.mp4",
        "created_at": datetime.now(timezone.utc),
        "progress": {"vision": 0.0, "audio": 0.0, "synthesis": 0.0},
        "error_message": None,
        "sos_timestamps": [], # SOS 없음
    }

    # 3. 서비스 실행
    print("[TEST] Starting VideoProcessingService...")
    print(f"  -> Task ID: {task_id}")
    print(f"  -> Processing Directory: {storage_path / 'processing' / task_id}")
    
    try:
        # 서비스 실행 (Direct Await)
        await VideoProcessingService.process_video_task(task_id, _task_store)
        
        task = _task_store[task_id]
        if task["status"] == "completed":
            print("\n[SUCCESS] Pipeline Completed!")
            print(f"  -> Progress: {task['progress']}")
            print(f"  -> Note Title: {task['note_data']['title']}")
            print(f"  -> Slides Count: {len(task['note_data']['slides'])}")
            
            # 중간 산출물 확인
            process_dir = storage_path / "processing" / task_id
            

            # 2. Slides
            slides = list((process_dir / "slides").glob("*.jpg"))
            print(f"  -> Unique Slides: {len(slides)} files at {process_dir / 'slides'}")
            
            # 3. Audio
            audio_file = process_dir / "audio.wav"
            if audio_file.exists():
                print(f"  -> Audio File: {audio_file} ({audio_file.stat().st_size / (1024*1024):.2f} MB)")
            else:
                print(f"  -> Audio File: MISSING")

            # 결과물 확인
            output_md = storage_path / "outputs" / task_id / "note.md"
            if output_md.exists():
                print(f"\n[OUTPUT] Markdown generated at: {output_md}")
                print("-" * 40)
                print(output_md.read_text(encoding="utf-8")[:500] + "\n...")
                print("-" * 40)
        else:
            print(f"\n[FAILED] Task status: {task['status']}")
            print(f"  -> Error: {task.get('error_message')}")

    except Exception as e:
        print(f"\n[CRITICAL ERROR] {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_integration())
